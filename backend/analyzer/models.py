from django.contrib.auth.models import AbstractUser
from django.db import models
from pymongo import MongoClient, ASCENDING, DESCENDING
from django.conf import settings
from datetime import datetime, timedelta
from bson import ObjectId

# ============= MongoDB Connection =============
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


# ============= User Model (Django) =============
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Stored in Django's default database (SQLite/PostgreSQL)
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


# ============= MongoDB Models =============

class UserProfile:
    """MongoDB model for user profiles and preferences"""
    collection_name = 'user_profiles'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        return db[cls.collection_name]
    
    @classmethod
    def create(cls, user_id, **kwargs):
        collection = cls.get_collection()
        profile = {
            'user_id': user_id,
            'favorite_categories': kwargs.get('favorite_categories', []),
            'notification_enabled': kwargs.get('notification_enabled', True),
            'notification_frequency': kwargs.get('notification_frequency', 'daily'),
            'notification_categories': kwargs.get('notification_categories', []),
            'theme': kwargs.get('theme', 'light'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = collection.insert_one(profile)
        profile['_id'] = str(result.inserted_id)
        return profile
    
    @classmethod
    def get_by_user_id(cls, user_id):
        collection = cls.get_collection()
        profile = collection.find_one({'user_id': user_id})
        if profile:
            profile['_id'] = str(profile['_id'])
        return profile
    
    @classmethod
    def update(cls, user_id, **kwargs):
        collection = cls.get_collection()
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        
        result = collection.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0


class NewsArticle:
    """MongoDB model for news articles"""
    collection_name = 'news_articles'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        collection = db[cls.collection_name]
        # Create indexes
        collection.create_index([('published_at', DESCENDING)])
        collection.create_index([('category', ASCENDING)])
        collection.create_index([('sentiment', ASCENDING)])
        collection.create_index([('url', ASCENDING)], unique=True)
        return collection
    
    @classmethod
    def create(cls, **kwargs):
        collection = cls.get_collection()
        article = {
            'title': kwargs.get('title'),
            'description': kwargs.get('description'),
            'content': kwargs.get('content'),
            'url': kwargs.get('url'),
            'image_url': kwargs.get('image_url'),
            'source': kwargs.get('source'),
            'author': kwargs.get('author'),
            'category': kwargs.get('category', 'general'),
            'sentiment': kwargs.get('sentiment'),
            'sentiment_confidence': kwargs.get('sentiment_confidence'),
            'published_at': kwargs.get('published_at', datetime.utcnow()),
            'fetched_at': datetime.utcnow(),
            'view_count': 0,
            'like_count': 0,
            'save_count': 0
        }
        try:
            result = collection.insert_one(article)
            article['_id'] = str(result.inserted_id)
            return article
        except Exception as e:
            # Handle duplicate URL
            if 'duplicate key error' in str(e).lower():
                return None
            raise e
    
    @classmethod
    def get_by_id(cls, article_id):
        collection = cls.get_collection()
        article = collection.find_one({'_id': ObjectId(article_id)})
        if article:
            article['_id'] = str(article['_id'])
            article['published_at'] = article['published_at'].isoformat() if isinstance(article['published_at'], datetime) else article['published_at']
        return article
    
    @classmethod
    def get_all(cls, filters=None, skip=0, limit=20, sort_by='published_at', sort_order=-1):
        collection = cls.get_collection()
        query = filters or {}
        
        articles = collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        result = []
        for article in articles:
            article['_id'] = str(article['_id'])
            article['published_at'] = article['published_at'].isoformat() if isinstance(article['published_at'], datetime) else article['published_at']
            result.append(article)
        return result
    
    @classmethod
    def count(cls, filters=None):
        collection = cls.get_collection()
        return collection.count_documents(filters or {})
    
    @classmethod
    def increment_view_count(cls, article_id):
        collection = cls.get_collection()
        result = collection.update_one(
            {'_id': ObjectId(article_id)},
            {'$inc': {'view_count': 1}}
        )
        return result.modified_count > 0
    
    @classmethod
    def increment_like_count(cls, article_id, increment=1):
        collection = cls.get_collection()
        result = collection.update_one(
            {'_id': ObjectId(article_id)},
            {'$inc': {'like_count': increment}}
        )
        return result.modified_count > 0
    
    @classmethod
    def increment_save_count(cls, article_id, increment=1):
        collection = cls.get_collection()
        result = collection.update_one(
            {'_id': ObjectId(article_id)},
            {'$inc': {'save_count': increment}}
        )
        return result.modified_count > 0


class Article:
    """Legacy model for sentiment analysis results"""
    collection_name = 'articles'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        return db[cls.collection_name]
    
    @classmethod
    def create(cls, text, sentiment, confidence):
        """Create a new article entry"""
        collection = cls.get_collection()
        article = {
            'text': text,
            'sentiment': sentiment,
            'confidence': float(confidence),
            'created_at': datetime.utcnow()
        }
        result = collection.insert_one(article)
        article['_id'] = str(result.inserted_id)
        return article
    
    @classmethod
    def get_recent(cls, limit=10):
        """Get recent articles"""
        collection = cls.get_collection()
        articles = collection.find().sort('created_at', -1).limit(limit)
        result = []
        for article in articles:
            article['_id'] = str(article['_id'])
            article['created_at'] = article['created_at'].isoformat()
            result.append(article)
        return result


class ArticleView:
    """Track article views by users"""
    collection_name = 'article_views'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        collection = db[cls.collection_name]
        collection.create_index([('user_id', ASCENDING), ('article_id', ASCENDING)])
        return collection
    
    @classmethod
    def create(cls, user_id, article_id):
        collection = cls.get_collection()
        view = {
            'user_id': user_id,
            'article_id': article_id,
            'timestamp': datetime.utcnow()
        }
        result = collection.insert_one(view)
        return result.inserted_id


class ArticleLike:
    """Track article likes by users"""
    collection_name = 'article_likes'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        collection = db[cls.collection_name]
        collection.create_index([('user_id', ASCENDING), ('article_id', ASCENDING)], unique=True)
        return collection
    
    @classmethod
    def toggle(cls, user_id, article_id):
        """Toggle like - return True if liked, False if unliked"""
        collection = cls.get_collection()
        existing = collection.find_one({'user_id': user_id, 'article_id': article_id})
        
        if existing:
            # Unlike
            collection.delete_one({'user_id': user_id, 'article_id': article_id})
            NewsArticle.increment_like_count(article_id, -1)
            return False
        else:
            # Like
            like = {
                'user_id': user_id,
                'article_id': article_id,
                'timestamp': datetime.utcnow()
            }
            collection.insert_one(like)
            NewsArticle.increment_like_count(article_id, 1)
            return True
    
    @classmethod
    def is_liked(cls, user_id, article_id):
        collection = cls.get_collection()
        return collection.find_one({'user_id': user_id, 'article_id': article_id}) is not None


class ArticleSave:
    """Track saved articles by users"""
    collection_name = 'article_saves'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        collection = db[cls.collection_name]
        collection.create_index([('user_id', ASCENDING), ('article_id', ASCENDING)], unique=True)
        return collection
    
    @classmethod
    def toggle(cls, user_id, article_id):
        """Toggle save - return True if saved, False if unsaved"""
        collection = cls.get_collection()
        existing = collection.find_one({'user_id': user_id, 'article_id': article_id})
        
        if existing:
            # Unsave
            collection.delete_one({'user_id': user_id, 'article_id': article_id})
            NewsArticle.increment_save_count(article_id, -1)
            return False
        else:
            # Save
            save = {
                'user_id': user_id,
                'article_id': article_id,
                'timestamp': datetime.utcnow()
            }
            collection.insert_one(save)
            NewsArticle.increment_save_count(article_id, 1)
            return True
    
    @classmethod
    def is_saved(cls, user_id, article_id):
        collection = cls.get_collection()
        return collection.find_one({'user_id': user_id, 'article_id': article_id}) is not None
    
    @classmethod
    def get_saved_articles(cls, user_id, skip=0, limit=20):
        collection = cls.get_collection()
        saves = collection.find({'user_id': user_id}).sort('timestamp', -1).skip(skip).limit(limit)
        
        article_ids = [save['article_id'] for save in saves]
        articles = []
        for article_id in article_ids:
            article = NewsArticle.get_by_id(article_id)
            if article:
                articles.append(article)
        return articles


class EmailLog:
    """Track sent emails to prevent duplicates"""
    collection_name = 'email_logs'
    
    @classmethod
    def get_collection(cls):
        db = MongoDB.get_instance()
        collection = db[cls.collection_name]
        collection.create_index([('user_id', ASCENDING), ('sent_at', DESCENDING)])
        return collection
    
    @classmethod
    def create(cls, user_id, email_type, article_ids):
        collection = cls.get_collection()
        log = {
            'user_id': user_id,
            'email_type': email_type,
            'article_ids': article_ids,
            'sent_at': datetime.utcnow()
        }
        result = collection.insert_one(log)
        return result.inserted_id
    
    @classmethod
    def get_last_sent(cls, user_id, email_type):
        collection = cls.get_collection()
        log = collection.find_one(
            {'user_id': user_id, 'email_type': email_type},
            sort=[('sent_at', DESCENDING)]
        )
        return log