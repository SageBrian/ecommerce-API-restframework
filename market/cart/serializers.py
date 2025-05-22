from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer, ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product', 
        queryset=Product.objects.all(),
        write_only=True
    )
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        source='variant',
        queryset=ProductVariant.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'subtotal']
    
    def validate(self, data):
        # Check if variant belongs to product
        product = data.get('product')
        variant = data.get('variant')
        
        if variant and variant.product != product:
            raise serializers.ValidationError("This variant does not belong to the specified product.")
        
        # Check stock availability
        requested_qty = data.get('quantity', 1)
        
        if variant:
            if variant.stock < requested_qty:
                raise serializers.ValidationError(f"Not enough stock available. Only {variant.stock} items available.")
        elif product.stock < requested_qty:
            raise serializers.ValidationError(f"Not enough stock available. Only {product.stock} items available.")
        
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']