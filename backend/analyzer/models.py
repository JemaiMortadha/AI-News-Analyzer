from pymongo import MongoClient
from django.conf import settings
from datetime import datetime

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

class Article:
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