from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AddressViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('', include(router.urls)),
]