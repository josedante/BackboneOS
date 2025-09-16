from rest_framework import serializers
from .models import (
    Country, Industry, FunctionOrResponsibility, Skill,
    PersonalIDType, OrganizationType, OrganizationalIDType,
    DescriptorFamily, WorldDescriptor, MarketSegment, Tag,
    AcademicDegree, Position, Gender, MaritalStatus
)


class CountrySerializer(serializers.ModelSerializer):
    """Serializer para países"""
    
    class Meta:
        model = Country
        fields = [
            'iso3_code', 'iso2_code', 'name', 'official_name',
            'phone_code', 'currency_code', 'timezone', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CountryListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de países"""
    
    class Meta:
        model = Country
        fields = ['iso3_code', 'iso2_code', 'name', 'phone_code']


class IndustrySerializer(serializers.ModelSerializer):
    """Serializer para industrias"""
    full_hierarchy_name = serializers.ReadOnlyField()
    sub_industries = serializers.StringRelatedField(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Industry
        fields = [
            'id', 'name', 'code', 'description', 'parent', 'parent_name',
            'ciiu_code', 'display_order', 'is_active',
            'full_hierarchy_name', 'sub_industries',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IndustryTreeSerializer(serializers.ModelSerializer):
    """Serializer para vista jerárquica de industrias"""
    sub_industries = serializers.SerializerMethodField()
    
    class Meta:
        model = Industry
        fields = ['id', 'name', 'code', 'description', 'sub_industries']
    
    def get_sub_industries(self, obj):
        if obj.sub_industries.exists():
            return IndustryTreeSerializer(
                obj.sub_industries.filter(is_active=True), 
                many=True
            ).data
        return []


class FunctionSerializer(serializers.ModelSerializer):
    """Serializer para funciones y responsabilidades"""
    sub_functions = serializers.StringRelatedField(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    typical_level_display = serializers.CharField(source='get_typical_level_display', read_only=True)
    
    class Meta:
        model = FunctionOrResponsibility
        fields = [
            'id', 'name', 'code', 'description', 'parent', 'parent_name',
            'typical_level', 'typical_level_display', 'display_order',
            'is_active', 'sub_functions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer para habilidades"""
    skill_type_display = serializers.CharField(source='get_skill_type_display', read_only=True)
    level_required_display = serializers.CharField(source='get_typical_level_required_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'code', 'description', 'skill_type', 'skill_type_display',
            'typical_level_required', 'level_required_display', 'display_order',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# TODO: Implementar modelo Topic
# class TopicSerializer(serializers.ModelSerializer):
#     """Serializer para temas"""
#     category_display = serializers.CharField(source='get_category_display', read_only=True)
#     sub_topics = serializers.StringRelatedField(many=True, read_only=True)
#     parent_name = serializers.CharField(source='parent.name', read_only=True)
#     
#     class Meta:
#         model = Topic
#         fields = [
#             'id', 'name', 'code', 'description', 'category', 'category_display',
#             'parent', 'parent_name', 'display_order', 'is_active',
#             'sub_topics', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']


class PersonalIDTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de documentos personales"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.iso2_code', read_only=True)
    
    class Meta:
        model = PersonalIDType
        fields = [
            'id', 'name', 'country', 'country_name', 'country_code', 'code',
            'regex_pattern', 'max_length', 'min_length', 'display_order',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de organizaciones"""
    ownership_type_display = serializers.CharField(source='get_ownership_type_display', read_only=True)
    typical_size_display = serializers.CharField(source='get_typical_size_display', read_only=True)
    
    class Meta:
        model = OrganizationType
        fields = [
            'id', 'name', 'code', 'description', 'ownership_type', 'ownership_type_display',
            'typical_size', 'typical_size_display', 'display_order',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationalIDTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de documentos organizacionales"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.iso2_code', read_only=True)
    
    class Meta:
        model = OrganizationalIDType
        fields = [
            'id', 'name', 'country', 'country_name', 'country_code', 'code',
            'regex_pattern', 'max_length', 'min_length', 'display_order',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DescriptorFamilySerializer(serializers.ModelSerializer):
    """Serializer para familias de descriptores"""
    descriptors_count = serializers.IntegerField(source='descriptors.count', read_only=True)
    
    class Meta:
        model = DescriptorFamily
        fields = [
            'code', 'name', 'description', 'is_active',
            'descriptors_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorldDescriptorSerializer(serializers.ModelSerializer):
    """Serializer para descriptores del mundo"""
    family_name = serializers.CharField(source='family.name', read_only=True)
    family_code = serializers.CharField(source='family.code', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = WorldDescriptor
        fields = [
            'id', 'family', 'family_name', 'family_code', 'name', 'code',
            'description', 'parent', 'parent_name', 'children',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarketSegmentSerializer(serializers.ModelSerializer):
    """Serializer para segmentos de mercado"""
    segment_type_display = serializers.CharField(source='get_segment_type_display', read_only=True)
    
    # Relaciones anidadas simplificadas
    industries = serializers.StringRelatedField(many=True, read_only=True)
    functions = serializers.StringRelatedField(many=True, read_only=True)
    skills = serializers.StringRelatedField(many=True, read_only=True)
    # topics = serializers.StringRelatedField(many=True, read_only=True)  # TODO: Implementar modelo Topic
    descriptors = serializers.StringRelatedField(many=True, read_only=True)
    
    # IDs para edición
    industry_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Industry.objects.filter(is_active=True),
        source='industries', write_only=True
    )
    function_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=FunctionOrResponsibility.objects.filter(is_active=True),
        source='functions', write_only=True
    )
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.filter(is_active=True),
        source='skills', write_only=True
    )
    # TODO: Implementar modelo Topic
    # topic_ids = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Topic.objects.filter(is_active=True),
    #     source='topics', write_only=True
    # )
    descriptor_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=WorldDescriptor.objects.filter(is_active=True),
        source='descriptors', write_only=True
    )
    
    class Meta:
        model = MarketSegment
        fields = [
            'id', 'name', 'code', 'description', 'segment_type', 'segment_type_display',
            'display_order', 'is_active',
            'industries', 'functions', 'skills', 'descriptors',  # 'topics',
            'industry_ids', 'function_ids', 'skill_ids', 'descriptor_ids',  # 'topic_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarketSegmentDetailSerializer(MarketSegmentSerializer):
    """Serializer detallado para segmentos de mercado"""
    industries = IndustrySerializer(many=True, read_only=True)
    functions = FunctionSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    # topics = TopicSerializer(many=True, read_only=True)  # TODO: Implementar modelo Topic
    descriptors = WorldDescriptorSerializer(many=True, read_only=True)


class TagSerializer(serializers.ModelSerializer):
    """Serializer para etiquetas"""
    
    class Meta:
        model = Tag
        fields = [
            'slug', 'name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AcademicDegreeSerializer(serializers.ModelSerializer):
    """Serializer para grados académicos"""
    class Meta:
        model = AcademicDegree
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AcademicDegreeChoiceSerializer(serializers.ModelSerializer):
    """Serializer simplificado para choices de grados académicos"""
    class Meta:
        model = AcademicDegree
        fields = ['id', 'name', 'code']


class PositionSerializer(serializers.ModelSerializer):
    """Serializer para posiciones/cargos"""
    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PositionChoiceSerializer(serializers.ModelSerializer):
    """Serializer simplificado para choices de posiciones"""
    class Meta:
        model = Position
        fields = ['id', 'name', 'code']


# Serializers simplificados para selecciones/dropdowns
class CountryChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['iso3_code', 'name']


class IndustryChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'code']


class FunctionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionOrResponsibility
        fields = ['id', 'name', 'code']


class SkillChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'skill_type']


class GenderSerializer(serializers.ModelSerializer):
    """Serializer para géneros"""
    class Meta:
        model = Gender
        fields = ['id', 'name', 'code', 'description', 'display_order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GenderChoiceSerializer(serializers.ModelSerializer):
    """Serializer simplificado para choices de géneros"""
    class Meta:
        model = Gender
        fields = ['id', 'name', 'code']


class MaritalStatusSerializer(serializers.ModelSerializer):
    """Serializer para estados civiles"""
    class Meta:
        model = MaritalStatus
        fields = ['id', 'name', 'code', 'description', 'display_order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaritalStatusChoiceSerializer(serializers.ModelSerializer):
    """Serializer simplificado para choices de estados civiles"""
    class Meta:
        model = MaritalStatus
        fields = ['id', 'name', 'code']


# TODO: Implementar modelo Topic
# class TopicChoiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Topic
#         fields = ['id', 'name', 'category']
