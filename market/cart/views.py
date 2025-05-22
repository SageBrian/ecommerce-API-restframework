from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_or_create_cart(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_or_create_cart()
        
        # Extract data from request
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        
        # Check if item already exists in cart
        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id,
                variant_id=variant_id
            )
            # Update quantity if item exists
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # Create new item if it doesn't exist
            serializer = CartItemSerializer(data={
                'product_id': product_id,
                'variant_id': variant_id,
                'quantity': quantity
            })
            
            if serializer.is_valid():
                serializer.save(cart=cart)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Return updated cart
        cart_serializer = self.get_serializer(cart)
        return Response(cart_serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        cart = self.get_or_create_cart()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
                
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_or_create_cart()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_or_create_cart()
        cart.items.all().delete()
        
        cart_serializer = self.get_serializer(cart)
        return Response(cart_serializer.data)