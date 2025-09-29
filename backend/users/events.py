import datetime
from django.conf import settings
from django.utils.timezone import now
from celery import shared_task
import uuid
import re
from .models import CriticalUserEvent

# Configuración para logging de actividad de usuario
# Basado en la configuración de Django, con opciones para MongoDB o DynamoDB

LOG_USER_ACTIVITY = getattr(settings, 'LOG_USER_ACTIVITY', False)
USE_ASYNC_LOGGING = getattr(settings, 'USE_CELERY', False)
LOG_ACTIVITY_BACKEND = getattr(settings, 'USER_ACTIVITY_BACKEND', 'mongodb')  # 'mongodb' or 'dynamodb'

# Validación de command_name para evitar caracteres conflictivos en MongoDB/DynamoDB
def validate_command_name(command_name: str) -> str:
    if not command_name:
        return None
    command_name = command_name.replace('$', '').replace('.', '_').replace(' ', '_')
    if not re.match(r'^[\w\-:]+$', command_name):
        raise ValueError(f"Invalid characters in command_name: {command_name}")
    return command_name

# Función principal a invocar desde cualquier lugar del backend
def log_user_activity(user, activity_type, description="", metadata=None, request=None):

    """
    Registra la actividad del usuario en la base de datos.
    :param user: Usuario que realiza la actividad (debe ser un objeto User).
    :param activity_type: Tipo de actividad (string).
    :param description: Descripción de la actividad (string).
    :param metadata: Diccionario opcional con metadatos adicionales.
    :param request: Objeto request para obtener IP y user agent (opcional).
    :raises ValueError: Si el usuario no está autenticado, o si los parámetros no son válidos.
    """

    # Validar tipo de evento crítico
    critical_types = [event[0] for event in getattr(CriticalUserEvent, "EVENT_TYPES", [])]
    is_critical = activity_type in critical_types

    if is_critical:
        # Validación estricta del usuario
        if not isinstance(user, User):
            raise ValueError("El parámetro `user` debe ser una instancia válida de User.")

        CriticalUserEvent.objects.create(
            user=user,
            event_type=activity_type,
            ip_address=getattr(request, 'META', {}).get('REMOTE_ADDR') if request else None,
            user_agent=getattr(request, 'META', {}).get('HTTP_USER_AGENT', '') if request else '',
            metadata=metadata or {},
        )

    if not LOG_USER_ACTIVITY:
        return
    if not user or not user.is_authenticated:
        raise ValueError("User must be authenticated to log activity.")
    if not activity_type:
        raise ValueError("Activity type must be provided.")
    if not isinstance(activity_type, str):
        raise ValueError("Activity type must be a string.")
    if not isinstance(description, str):
        raise ValueError("Description must be a string.")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary if provided.")
    # if not isinstance(user, user.__class__):
    #     raise ValueError("User must be an instance of the User model.")
    # if not hasattr(user, 'get_username'):
    #     raise ValueError("User model must implement get_username method.")
    # if not hasattr(user, 'id'):
    #     raise ValueError("User model must have an 'id' attribute.")
    # if not hasattr(user, 'is_authenticated'):
    #     raise ValueError("User model must have an 'is_authenticated' attribute.")
    
    command_name = metadata.get("command_name") if metadata else None
    validated_command_name = validate_command_name(command_name) if command_name else None

    payload = {
        "activity_uuid": str(uuid.uuid4()),
        "user_id": str(user.id),
        "username": user.get_username(),
        "activity_type": activity_type,
        "description": description,
        "timestamp": now().isoformat(),
        "metadata": metadata or {},
        "ip": getattr(request, 'META', {}).get('REMOTE_ADDR') if request else None,
        "user_agent": getattr(request, 'META', {}).get('HTTP_USER_AGENT') if request else None,
        "source": 'web',
        # Elementos adicionales inspirados en estructura anterior
        "trigger_context": metadata.get("trigger_context") if metadata else None,  # como "touchpoint_type_identifier"
        "related_object_uuid": metadata.get("related_object_uuid") if metadata else None,  # como "touchpoint_uuid"
        "command_name": validated_command_name,
    }

    if USE_ASYNC_LOGGING:
        persist_activity_event.delay(payload)
    else:
        persist_activity_event(payload)


@shared_task
def persist_activity_event(payload):
    if LOG_ACTIVITY_BACKEND == 'dynamodb':
        persist_to_dynamodb(payload)
    else:
        persist_to_mongodb(payload)


def persist_to_mongodb(payload):
    from pymongo import MongoClient
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    collection = db['user_activity_logs']
    collection.insert_one(payload)
    client.close()


def persist_to_dynamodb(payload):
    import boto3
    from botocore.exceptions import ClientError
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DYNAMODB_REGION,
            endpoint_url=getattr(settings, 'AWS_DYNAMODB_ENDPOINT', None)
        )
        table = dynamodb.Table(getattr(settings, 'AWS_USER_ACTIVITY_TABLE', 'UserActivityLogs'))
        item = {
            "activity_uuid": payload.get("activity_uuid"),
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "activity_type": payload.get("activity_type"),
            "description": payload.get("description", ""),
            "timestamp": payload.get("timestamp"),
            "ip": payload.get("ip"),
            "user_agent": payload.get("user_agent"),
            "source": payload.get("source", "web"),
            "metadata": payload.get("metadata", {}),
            "trigger_context": payload.get("trigger_context"),
            "related_object_uuid": payload.get("related_object_uuid"),
            "command_name": payload.get("command_name"),
        }
        table.put_item(Item=item)
    except ClientError as e:
        import bugsnag
        bugsnag.notify(e, meta_data={"payload": payload})
