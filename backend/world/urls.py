from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router principal
router = DefaultRouter()

# Registro de ViewSets
router.register(r'countries', views.CountryViewSet)
router.register(r'industries', views.IndustryViewSet, basename='industry')
router.register(r'functions', views.FunctionViewSet, basename='function')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'personal-id-types', views.PersonalIDTypeViewSet, basename='personal-id-type')
router.register(r'organization-types', views.OrganizationTypeViewSet, basename='organization-type')
router.register(r'organizational-id-types', views.OrganizationalIDTypeViewSet, basename='organizational-id-type')
router.register(r'descriptor-families', views.DescriptorFamilyViewSet, basename='descriptor-family')
router.register(r'world-descriptors', views.WorldDescriptorViewSet, basename='world-descriptor')
router.register(r'market-segments', views.MarketSegmentViewSet, basename='market-segment')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'academic-degrees', views.AcademicDegreeViewSet, basename='academic-degree')
router.register(r'positions', views.PositionViewSet, basename='position')
router.register(r'genders', views.GenderViewSet, basename='gender')
router.register(r'marital-statuses', views.MaritalStatusViewSet, basename='marital-status')
router.register(r'choices', views.WorldChoicesViewSet, basename='world-choices')

app_name = 'world'

urlpatterns = [
    path('', include(router.urls)),
]

# URLs adicionales para endpoints específicos
urlpatterns += [
    # Endpoints personalizados si los necesitas
    # path('custom-endpoint/', views.custom_view, name='custom-endpoint'),
]
