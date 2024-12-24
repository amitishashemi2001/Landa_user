from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError
import re

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'mobile', 'first_name', 'last_name', 'password']

    def validate_mobile(self, value):
        if not re.match(r'^(\+98|0)?9\d{9}$', value):
            raise ValidationError("Mobile number must start with +98 or 0 and followed by 9 and 9 digits.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
