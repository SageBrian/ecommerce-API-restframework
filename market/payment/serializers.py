from rest_framework import serializers
from .models import Payment, PaymentMethod
from orders.models import Order

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'card_type', 'last_four_digits', 'expiry_month', 'expiry_year', 'is_default']
        read_only_fields = ['id']

class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.ReadOnlyField(source='order.id')
    user = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'amount', 'payment_method', 'status',
            'transaction_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_method_id = serializers.IntegerField(required=False)
    
    def validate_order_id(self, value):
        user = self.context['request'].user
        try:
            order = Order.objects.get(id=value, user=user)
            if order.payment_status:
                raise serializers.ValidationError("Order is already paid.")
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
    
    def validate_payment_method_id(self, value):
        if value:
            user = self.context['request'].user
            try:
                return PaymentMethod.objects.get(id=value, user=user)
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError("Payment method not found.")
        return None
    
    def create(self, validated_data):
        user = self.context['request'].user
        order = validated_data['order_id']
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=order.total_price,
            payment_method=validated_data['payment_method'],
            status='processing'
        )
        
        # Simulate payment processing
        # In real implementation, integrate with payment gateway
        success = self.process_payment(payment, validated_data.get('payment_method_id'))
        
        if success:
            payment.status = 'completed'
            payment.transaction_id = f"txn_{payment.id}"
            order.payment_status = True
            order.status = 'processing'
        else:
            payment.status = 'failed'
        
        payment.save()
        order.save()
        
        return payment
    
    def process_payment(self, payment, payment_method_id):
        # Simulate payment processing
        # In real implementation, integrate with Stripe, PayPal, etc.
        import random
        return random.choice([True, True, True, False])  # 75% success rate for demo