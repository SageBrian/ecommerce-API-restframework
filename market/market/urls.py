from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.cof.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users',include('users.urls')),
    path('api/products',include('products.urls')),
    path('api/orders',include('orders.urls')),
    path('api/cart',include('cart.urls')),
    path('api/payment',include('payment.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    