from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer
)
from .models import UserProfile


# ============= Authentication Views =============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user
    POST /api/auth/register/
    Body: { "email": "user@example.com", "username": "username", "password": "pass123", "password2": "pass123" }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'User registered successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user
    POST /api/auth/login/
    Body: { "email": "user@example.com", "password": "pass123" }
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'Login successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update user profile
    GET /api/auth/profile/
    PUT /api/auth/profile/
    Body: { "favorite_categories": ["technology", "sports"], "notification_enabled": true }
    """
    user = request.user
    
    if request.method == 'GET':
        # Get Django user data
        user_data = UserSerializer(user).data
        
        # Get MongoDB profile data
        profile = UserProfile.get_by_user_id(user.id)
        if not profile:
            profile = UserProfile.create(user_id=user.id)
        
        return Response({
            'user': user_data,
            'profile': profile
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update profile
        UserProfile.update(user.id, **serializer.validated_data)
        
        # Get updated profile
        profile = UserProfile.get_by_user_id(user.id)
        
        return Response({
            'profile': profile,
            'message': 'Profile updated successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user (blacklist refresh token)
    POST /api/auth/logout/
    Body: { "refresh": "refresh_token" }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

# ============= Password Reset Views =============

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset - sends email with reset token
    POST /api/auth/password-reset/request/
    Body: { "email": "user@example.com" }
    """
    from .models import User
    from .password_reset import PasswordResetToken
    from .email_service import send_password_reset_email
    
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = PasswordResetToken.create(user.id, email)
        
        # Send email with reset link
        reset_url = f"http://localhost:3000/reset-password/{token}"
        send_password_reset_email(email, user.username, reset_url)
        
        return Response({
            'message': 'Password reset email sent successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # Don't reveal if email exists or not (security)
        return Response({
            'message': 'If an account with that email exists, a password reset link has been sent'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirm password reset with token and new password
    POST /api/auth/password-reset/confirm/
    Body: { "token": "abc123", "password": "newpass123", "password2": "newpass123" }
    """
    from .models import User
    from .password_reset import PasswordResetToken
    from django.contrib.auth.hashers import make_password
    
    token = request.data.get('token')
    password = request.data.get('password')
    password2 = request.data.get('password2')
    
    if not all([token, password, password2]):
        return Response(
            {'error': 'Token and passwords are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if password != password2:
        return Response(
            {'error': 'Passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token
    reset_token = PasswordResetToken.verify(token)
    
    if not reset_token:
        return Response(
            {'error': 'Invalid or expired reset token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Update user password
        user = User.objects.get(id=reset_token['user_id'])
        user.password = make_password(password)
        user.save()
        
        # Mark token as used
        PasswordResetToken.mark_as_used(token)
        
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
