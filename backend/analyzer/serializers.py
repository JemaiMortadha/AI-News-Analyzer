from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

# ============= Authentication Serializers =============

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        # Create user profile in MongoDB
        UserProfile.create(user_id=user.id)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'created_at')
        read_only_fields = ('created_at',)


class UserProfileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(read_only=True)
    favorite_categories = serializers.ListField(child=serializers.CharField(), required=False)
    notification_enabled = serializers.BooleanField(required=False)
    notification_frequency = serializers.ChoiceField(choices=['daily', 'weekly'], required=False)
    notification_categories = serializers.ListField(child=serializers.CharField(), required=False)
    theme = serializers.ChoiceField(choices=['light', 'dark'], required=False)


# ============= News Serializers =============

class NewsArticleSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    url = serializers.URLField()
    image_url = serializers.URLField(required=False, allow_null=True)
    source = serializers.CharField()
    author = serializers.CharField(required=False, allow_null=True)
    category = serializers.CharField(required=False)
    sentiment = serializers.CharField(required=False, allow_null=True)
    sentiment_confidence = serializers.FloatField(required=False, allow_null=True)
    published_at = serializers.CharField(required=False)
    view_count = serializers.IntegerField(read_only=True, default=0)
    like_count = serializers.IntegerField(read_only=True, default=0)
    save_count = serializers.IntegerField(read_only=True, default=0)
    is_liked = serializers.BooleanField(read_only=True, default=False)
    is_saved = serializers.BooleanField(read_only=True, default=False)


# ============= Legacy Serializers =============

class AnalyzeRequestSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False)

class AnalyzeResponseSerializer(serializers.Serializer):
    sentiment = serializers.CharField()
    confidence = serializers.FloatField()

class ArticleSerializer(serializers.Serializer):
    _id = serializers.CharField()
    text = serializers.CharField()
    sentiment = serializers.CharField()
    confidence = serializers.FloatField()
    created_at = serializers.CharField()