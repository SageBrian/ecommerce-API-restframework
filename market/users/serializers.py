from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'street_address', 'apartment_address', 
                  'city', 'state', 'country', 'postal_code', 'default']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth', 'addresses', 'is_verified']
        read_only_fields = ['is_verified']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirmation']
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirmation'):
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)