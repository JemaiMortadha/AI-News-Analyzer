import secrets
from datetime import datetime, timedelta
from pymongo import MongoClient
from django.conf import settings

class MongoDB:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            client = MongoClient(
                host=settings.MONGODB_HOST,
                port=settings.MONGODB_PORT
            )
            cls._instance = client[settings.MONGODB_NAME]
        return cls._instance


class PasswordResetToken:
    """MongoDB model for password reset tokens"""
    collection_name = 'password_reset_tokens'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        return db[cls.collection_name]
    
    @classmethod
    def create(cls, user_id, email):
        """Create a new password reset token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        reset_data = {
            'user_id': user_id,
            'email': email,
            'token': token,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
            'used': False
        }
        
        cls.get_collection().insert_one(reset_data)
        return token
    
    @classmethod
    def verify(cls, token):
        """Verify if token is valid and not expired"""
        reset_token = cls.get_collection().find_one({
            'token': token,
            'used': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        return reset_token
    
    @classmethod
    def mark_as_used(cls, token):
        """Mark token as used after successful password reset"""
        cls.get_collection().update_one(
            {'token': token},
            {'$set': {'used': True}}
        )
    
    @classmethod
    def delete_expired(cls):
        """Delete all expired tokens (cleanup task)"""
        cls.get_collection().delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
