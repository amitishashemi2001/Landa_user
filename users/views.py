from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import SignupSerializer
from rest_framework.permissions import BasePermission
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import Permission
import random
import string

def generate_verification_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class CanEditNamePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.can_edit_name')


class CanEditIDPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.can_edit_id')


class SignupView(APIView):
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=SignupSerializer,
        responses={201: "User registered successfully!"}
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # اضافه کردن پرمیشن‌ها به کاربر
            edit_name_perm = Permission.objects.get(codename='can_edit_name')
            edit_id_perm = Permission.objects.get(codename='can_edit_id')

            # اختصاص پرمیشن‌ها به کاربر
            user.user_permissions.add(edit_name_perm, edit_id_perm)
            user.save()

            token = generate_verification_token()
            user.verify_code = token
            user.save()

            return Response({
                "message": "User registered successfully! Verify your account using the token.",
                "token": token
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Verify a user's token",
        request_body=serializers.Serializer,
        responses={200: "User verified successfully", 400: "Invalid token"}
    )
    def post(self, request):
        email = request.data.get('email')
        token_value = request.data.get('token')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        if user.verify_code != token_value:
            return Response({'error': 'Invalid token'}, status=400)

        user.is_active = True
        user.save()

        user.verify_code = ''
        user.save()

        return Response({'message': 'User verified successfully'})


class UpdateNameAndIDView(APIView):
    @swagger_auto_schema(
        operation_description="Update user's name and/or ID",
        request_body=serializers.Serializer,
        responses={200: "Name and/or ID updated successfully", 403: "Permission denied", 404: "User not found"}
    )
    def post(self, request):
        if 'first_name' in request.data and not request.user.has_perm('users.can_edit_name'):
            return Response({'error': 'Permission denied to edit name'}, status=403)

        if 'id' in request.data and not request.user.has_perm('users.can_edit_id'):
            return Response({'error': 'Permission denied to edit ID'}, status=403)

        try:
            user = User.objects.get(pk=request.user.id)
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']  # تغییر نام
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'id' in request.data:
                user.id = request.data['id']
            user.save()

            return Response({'message': 'Name and/or ID updated successfully'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
