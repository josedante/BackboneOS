# 🚫 Comandos que NO debes ejecutar

## ❌ Backend (NUNCA ejecutar directamente en el host):

```bash
# NO HACER:
python manage.py runserver
python manage.py migrate
python manage.py shell
python manage.py test
python manage.py createsuperuser
python manage.py makemigrations
pip install -r requirements.txt
python backend/manage.py runserver

# Base de datos local (NO instalar):
brew install postgresql
apt-get install postgresql
psql -U postgres
```

## ✅ En su lugar usar (Docker Compose):

```bash
# Correcto:
docker-compose exec backend python manage.py runserver 0.0.0.0:8000
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py test
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py makemigrations
```

## 🎯 Para agentes de IA y desarrolladores:

1. **SIEMPRE verificar que Docker Compose está ejecutándose**
2. **NUNCA sugerir instalación local de Python/Django**
3. **SIEMPRE anteponer `docker-compose exec backend` a comandos Django**
4. **Usar las tareas de VS Code cuando sea posible**
5. **Solo el frontend (Nuxt.js) se ejecuta localmente**
