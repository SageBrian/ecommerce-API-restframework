from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer, ProductVariantSerializer
from users.serializers import AddressSerializer
from cart.models import Cart

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'quantity', 'price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.email')
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'shipping_address', 'billing_address',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_price',
            'payment_status', 'payment_method', 'tracking_number', 'notes',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField()
    
    class Meta:
        model = Order
        fields = ['shipping_address_id', 'billing_address_id', 'notes']
    
    def validate_shipping_address_id(self, value):
        user = self.context['request'].user
        try:
            address = user.addresses.get(id=value, address_type='S')
            return address
        except:
            raise serializers.ValidationError("Invalid shipping address.")
    
    def validate_billing_address_id(self, value):
        user = self.context['request'].user
        try:
            address = user.addresses.get(id=value, address_type='B')
            return address
        except:
            raise serializers.ValidationError("Invalid billing address.")
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty.")
        
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        
        # Calculate totals
        subtotal = cart.total_price
        tax_amount = subtotal * 0.08  # 8% tax
        shipping_cost = 10.00 if subtotal < 50 else 0.00  # Free shipping over $50
        total_price = subtotal + tax_amount + shipping_cost
        
        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address_id'],
            billing_address=validated_data['billing_address_id'],
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_price=total_price,
            notes=validated_data.get('notes', '')
        )
        
        # Create order items and reduce stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
            
            # Reduce stock
            if cart_item.variant:
                cart_item.variant.stock -= cart_item.quantity
                cart_item.variant.save()
            else:
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        return order