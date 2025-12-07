"""
Recommendation System for AI News Analyzer
Analyzes user interactions to provide personalized news recommendations
"""

from .models import UserInteraction, NewsArticle
from collections import defaultdict, Counter
from datetime import datetime, timedelta


class RecommendationEngine:
    """Engine for generating personalized news recommendations"""
    
    @staticmethod
    def get_user_category_preferences(user_id, days=30):
        """
        Analyze user interactions to determine category preferences
        Returns dict with category weights based on interaction types
        """
        interactions = UserInteraction.get_by_user(user_id)
        
        if not interactions:
            return {}
        
        # Weight different interaction types
        WEIGHTS = {
            'save': 5,    # Saves are strongest signal
            'like': 3,    # Likes are medium signal
            'view': 1     # Views are weakest signal
        }
        
        category_scores = defaultdict(float)
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        for interaction in interactions:
            # Skip old interactions
            if interaction.get('created_at', datetime.min) < cutoff_date:
                continue
                
            article_id = interaction.get('article_id')
            interaction_type = interaction.get('interaction_type')
            
            # Get article to find its category
            article = NewsArticle.get_by_id(article_id)
            if article and 'category' in article:
                category = article['category']
                weight = WEIGHTS.get(interaction_type, 1)
                category_scores[category] += weight
        
        # Normalize scores to percentages
        total_score = sum(category_scores.values())
        if total_score > 0:
            category_preferences = {
                cat: round((score / total_score) * 100, 2)
                for cat, score in category_scores.items()
            }
            # Sort by preference
            return dict(sorted(category_preferences.items(), key=lambda x: x[1], reverse=True))
        
        return {}
    
    @staticmethod
    def get_recommended_articles(user_id, limit=20):
        """
        Get personalized article recommendations for a user
        
        Algorithm:
        1. Get user's category preferences
        2. Fetch recent articles from preferred categories
        3. Exclude already viewed/saved articles
        4. Prioritize by sentiment and recency
        """
        # Get user preferences
        category_prefs = RecommendationEngine.get_user_category_preferences(user_id)
        
        if not category_prefs:
            # New user or no interactions - return trending articles
            return NewsArticle.get_all(
                filters={
                    'published_at': {'$gte': datetime.utcnow() - timedelta(days=7)}
                },
                limit=limit,
                sort_by='sentiment_confidence'
            )
        
        # Get user's interaction history to exclude seen articles
        interactions = UserInteraction.get_by_user(user_id)
        viewed_article_ids = {inter.get('article_id') for inter in interactions}
        
        # Get top 3 preferred categories
        top_categories = list(category_prefs.keys())[:3]
        
        recommended = []
        per_category_limit = limit // len(top_categories) + 1
        
        for category in top_categories:
            # Get recent articles from this category
            articles = NewsArticle.get_all(
                filters={
                    'category': category,
                    'published_at': {'$gte': datetime.utcnow() - timedelta(days=7)},
                    '_id': {'$nin': list(viewed_article_ids)}  # Exclude viewed
                },
                limit=per_category_limit,
                sort_by='published_at'
            )
            recommended.extend(articles)
        
        # If not enough articles, fill with general trending
        if len(recommended) < limit:
            additional = NewsArticle.get_all(
                filters={
                    'published_at': {'$gte': datetime.utcnow() - timedelta(days=7)},
                    '_id': {'$nin': list(viewed_article_ids)}
                },
                limit=limit - len(recommended),
                sort_by='sentiment_confidence'
            )
            recommended.extend(additional)
        
        return recommended[:limit]
    
    @staticmethod
    def get_similar_articles(article_id, limit=5):
        """
        Get articles similar to a given article
        Based on category and sentiment
        """
        article = NewsArticle.get_by_id(article_id)
        
        if not article:
            return []
        
        # Find articles with same category and similar sentiment
        similar = NewsArticle.get_all(
            filters={
                'category': article.get('category'),
                'sentiment': article.get('sentiment'),
                '_id': {'$ne': article_id}  # Exclude the article itself
            },
            limit=limit,
            sort_by='published_at'
        )
        
        return similar


def get_personalized_feed(user_id, page=1, limit=20):
    """
    Get personalized news feed for a user
    Wrapper function for easy use in views
    """
    engine = RecommendationEngine()
    return engine.get_recommended_articles(user_id, limit=limit)
