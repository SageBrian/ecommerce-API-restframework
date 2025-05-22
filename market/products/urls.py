from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, 
    ProductImageViewSet, ProductVariantViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', ProductViewSet)

# Nested routes
product_images_router = DefaultRouter()
product_images_router.register(r'images', ProductImageViewSet, basename='product-images')

product_variants_router = DefaultRouter()
product_variants_router.register(r'variants', ProductVariantViewSet, basename='product-variants')

product_reviews_router = DefaultRouter()
product_reviews_router.register(r'reviews', ReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('<slug:product_slug>/', include(product_images_router.urls)),
    path('<slug:product_slug>/', include(product_variants_router.urls)),
    path('<slug:product_slug>/', include(product_reviews_router.urls)),
]