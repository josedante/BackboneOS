from rest_framework import serializers
from .models import ProductOffering
from products.serializers import ProductListSerializer
from world.serializers import (
    IndustryChoiceSerializer, FunctionChoiceSerializer, 
    SkillChoiceSerializer, CountryChoiceSerializer,
    AcademicDegreeChoiceSerializer, PositionChoiceSerializer
)
from interactions.serializers import ChannelChoiceSerializer


class ProductOfferingListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de ofertas"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    price_display = serializers.CharField(read_only=True)
    is_currently_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ProductOffering
        fields = [
            'id', 'name', 'code', 'description', 'product_name', 'product_code',
            'price', 'currency_code', 'price_display', 'valid_from', 'valid_until',
            'auto_renew', 'duration_days', 'landing_url', 'is_currently_valid',
            'is_active', 'created_at', 'updated_at'
        ]


class ProductOfferingDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de ofertas"""
    product = ProductListSerializer(read_only=True)
    price_display = serializers.CharField(read_only=True)
    is_currently_valid = serializers.BooleanField(read_only=True)
    
    # Relaciones semánticas disponibles
    channels = ChannelChoiceSerializer(many=True, read_only=True)
    related_industries = IndustryChoiceSerializer(many=True, read_only=True)
    related_functions = FunctionChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductOffering
        fields = '__all__'


class ProductOfferingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para creación y actualización"""
    
    class Meta:
        model = ProductOffering
        fields = [
            'name', 'code', 'description', 'product', 'price', 'currency_code',
            'valid_from', 'valid_until', 'auto_renew', 'duration_days',
            'landing_url', 'channels', 'seats', 'target_segments',
            'related_industries', 'related_functions', 'descriptors', 'tags',
            'metadata', 'is_active'
        ]
    
    def validate_code(self, value):
        """Validar que el código sea único"""
        if self.instance:
            # En actualización, excluir la instancia actual
            if ProductOffering.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe una oferta con este código.")
        else:
            # En creación, verificar que no exista
            if ProductOffering.objects.filter(code=value).exists():
                raise serializers.ValidationError("Ya existe una oferta con este código.")
        return value
    
    def validate(self, data):
        """Validaciones de negocio"""
        valid_from = data.get('valid_from')
        valid_until = data.get('valid_until')
        
        if valid_from and valid_until and valid_from > valid_until:
            raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        price = data.get('price')
        if price and price <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero.")
        
        return data


class ProductOfferingChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices en formularios"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductOffering
        fields = ['id', 'name', 'code', 'display_name', 'price', 'currency_code']
    
    def get_display_name(self, obj):
        return f"{obj.name} - {obj.price_display}"


class ProductOfferingAnalyticsSerializer(serializers.Serializer):
    """Serializer para analytics de ofertas"""
    total_offerings = serializers.IntegerField()
    active_offerings = serializers.IntegerField()
    expired_offerings = serializers.IntegerField()
    future_offerings = serializers.IntegerField()
    
    by_currency = serializers.ListField()
    by_product_category = serializers.ListField()
    by_channel = serializers.ListField()
    by_market_segment = serializers.ListField()
    
    price_statistics = serializers.DictField()
    duration_statistics = serializers.DictField()
    
    top_products = serializers.ListField()
    recent_offerings = serializers.ListField()
