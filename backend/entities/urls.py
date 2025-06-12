from django.urls import path, include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'people', views.PersonViewSet, basename='person')
router.register(r'contacts', views.ContactDetailViewSet, basename='contact-detail')
router.register(r'profiles', views.IndividualProfileViewSet, basename='individual-profile')
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'addresses', views.PhysicalAddressViewSet, basename='physical-address')
router.register(r'choices', views.EntitiesChoicesViewSet, basename='entities-choices')

app_name = 'entities'

urlpatterns = [
    path('', include(router.urls)),
]

# URLs adicionales para endpoints personalizados si se necesitan
urlpatterns += [
    # Endpoints personalizados pueden ir aquí
    # path('custom-endpoint/', views.custom_view, name='custom-endpoint'),
]
