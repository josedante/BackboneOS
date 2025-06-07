from rest_framework import serializers
from world.serializers import (
    IndustrySerializer, SkillSerializer, MarketSegmentSerializer,
    FunctionSerializer, WorldDescriptorSerializer, TagSerializer
)
from .models import Division, ProductCategory, Modality, Customization, Product


class DivisionSerializer(serializers.ModelSerializer):
    categories_count = serializers.ReadOnlyField()
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Division
        fields = [
            'id', 'name', 'code', 'description', 'categories_count', 
            'products_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    level = serializers.ReadOnlyField()
    absolute_level = serializers.ReadOnlyField()
    subcategories_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'code', 'description', 'division', 'division_name',
            'parent', 'parent_name', 'full_path', 'level', 'absolute_level',
            'subcategories_count', 'products_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_subcategories_count(self, obj):
        return obj.subcategories.filter(is_active=True).count()

    def get_products_count(self, obj):
        return obj.product_set.filter(is_active=True).count()


class ProductCategoryTreeSerializer(ProductCategorySerializer):
    """Serializer para mostrar categorías con sus subcategorías"""
    subcategories = serializers.SerializerMethodField()

    class Meta(ProductCategorySerializer.Meta):
        fields = ProductCategorySerializer.Meta.fields + ['subcategories']

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True)
        return ProductCategorySerializer(subcategories, many=True, context=self.context).data


class ModalitySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Modality
        fields = ['id', 'name', 'description', 'products_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.product_set.filter(is_active=True).count()


class CustomizationSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Customization
        fields = ['id', 'name', 'description', 'products_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.product_set.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de productos"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_full_path = serializers.CharField(source='category.full_path', read_only=True)
    customization_name = serializers.CharField(source='customization.name', read_only=True)
    
    # Propiedades calculadas
    price_display = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    target_audience = serializers.SerializerMethodField()
    modalities_display = serializers.SerializerMethodField()
    has_canonical_url = serializers.ReadOnlyField()
    
    # Contadores
    skills_count = serializers.SerializerMethodField()
    industries_count = serializers.SerializerMethodField()
    segments_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'canonical_url', 'category', 'category_name', 
            'category_full_path', 'customization_name', 'duration', 'base_price', 
            'currency_code', 'price_display', 'duration_display', 'target_audience',
            'modalities_display', 'has_canonical_url', 'skills_count', 'industries_count', 'segments_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_target_audience(self, obj):
        return obj.get_target_audience()

    def get_modalities_display(self, obj):
        return obj.get_modalities_display()

    def get_skills_count(self, obj):
        return obj.related_skills.count()

    def get_industries_count(self, obj):
        return obj.related_industries.count()

    def get_segments_count(self, obj):
        return obj.target_segments.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de productos"""
    # Relaciones anidadas
    category = ProductCategorySerializer(read_only=True)
    modalities = ModalitySerializer(many=True, read_only=True)
    customization = CustomizationSerializer(read_only=True)
    
    # Relaciones del mundo
    target_segments = MarketSegmentSerializer(many=True, read_only=True)
    related_industries = IndustrySerializer(many=True, read_only=True)
    related_functions = FunctionSerializer(many=True, read_only=True)
    related_skills = SkillSerializer(many=True, read_only=True)
    descriptors = WorldDescriptorSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    # Propiedades calculadas
    price_display = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    is_customizable = serializers.ReadOnlyField()
    has_canonical_url = serializers.ReadOnlyField()
    skills_summary = serializers.SerializerMethodField()
    
    # IDs para escritura
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    modalities_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    customization_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    target_segments_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    related_industries_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    related_functions_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    related_skills_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    descriptors_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    tags_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'canonical_url', 'category', 'category_id',
            'modalities', 'modalities_ids', 'customization', 'customization_id',
            'duration', 'base_price', 'currency_code', 'target_segments',
            'target_segments_ids', 'related_industries', 'related_industries_ids',
            'related_functions', 'related_functions_ids', 'related_skills',
            'related_skills_ids', 'descriptors', 'descriptors_ids', 'tags',
            'tags_ids', 'price_display', 'duration_display', 'is_customizable',
            'has_canonical_url', 'skills_summary', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_skills_summary(self, obj):
        return obj.get_related_skills_summary()

    def create(self, validated_data):
        # Extraer IDs de relaciones M2M
        modalities_ids = validated_data.pop('modalities_ids', [])
        target_segments_ids = validated_data.pop('target_segments_ids', [])
        related_industries_ids = validated_data.pop('related_industries_ids', [])
        related_functions_ids = validated_data.pop('related_functions_ids', [])
        related_skills_ids = validated_data.pop('related_skills_ids', [])
        descriptors_ids = validated_data.pop('descriptors_ids', [])
        tags_ids = validated_data.pop('tags_ids', [])
        
        # Asignar IDs de FK
        if 'category_id' in validated_data:
            validated_data['category_id'] = validated_data.pop('category_id')
        if 'customization_id' in validated_data:
            validated_data['customization_id'] = validated_data.pop('customization_id')

        # Crear producto
        product = Product.objects.create(**validated_data)
        
        # Asignar relaciones M2M
        if modalities_ids:
            product.modalities.set(modalities_ids)
        if target_segments_ids:
            product.target_segments.set(target_segments_ids)
        if related_industries_ids:
            product.related_industries.set(related_industries_ids)
        if related_functions_ids:
            product.related_functions.set(related_functions_ids)
        if related_skills_ids:
            product.related_skills.set(related_skills_ids)
        if descriptors_ids:
            product.descriptors.set(descriptors_ids)
        if tags_ids:
            product.tags.set(tags_ids)

        return product

    def update(self, instance, validated_data):
        # Extraer IDs de relaciones M2M
        modalities_ids = validated_data.pop('modalities_ids', None)
        target_segments_ids = validated_data.pop('target_segments_ids', None)
        related_industries_ids = validated_data.pop('related_industries_ids', None)
        related_functions_ids = validated_data.pop('related_functions_ids', None)
        related_skills_ids = validated_data.pop('related_skills_ids', None)
        descriptors_ids = validated_data.pop('descriptors_ids', None)
        tags_ids = validated_data.pop('tags_ids', None)
        
        # Asignar IDs de FK
        if 'category_id' in validated_data:
            instance.category_id = validated_data.pop('category_id')
        if 'customization_id' in validated_data:
            instance.customization_id = validated_data.pop('customization_id')

        # Actualizar campos regulares
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar relaciones M2M
        if modalities_ids is not None:
            instance.modalities.set(modalities_ids)
        if target_segments_ids is not None:
            instance.target_segments.set(target_segments_ids)
        if related_industries_ids is not None:
            instance.related_industries.set(related_industries_ids)
        if related_functions_ids is not None:
            instance.related_functions.set(related_functions_ids)
        if related_skills_ids is not None:
            instance.related_skills.set(related_skills_ids)
        if descriptors_ids is not None:
            instance.descriptors.set(descriptors_ids)
        if tags_ids is not None:
            instance.tags.set(tags_ids)

        return instance


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear/actualizar productos"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'description', 'canonical_url', 'category', 'modalities',
            'customization', 'duration', 'base_price', 'currency_code',
            'target_segments', 'related_industries', 'related_functions',
            'related_skills', 'descriptors', 'tags', 'is_active'
        ]

    def validate_code(self, value):
        """Validar que el código sea único"""
        if self.instance and self.instance.code == value:
            return value
        
        if Product.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe un producto con este código.")
        return value

    def validate_base_price(self, value):
        """Validar que el precio sea positivo"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value
