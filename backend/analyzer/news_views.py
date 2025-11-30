from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import NewsArticle, ArticleView, ArticleLike, ArticleSave
from .serializers import NewsArticleSerializer
from .news_fetcher import NewsAggregator
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_list(request):
    """
    Get news articles with filtering and pagination
    GET /api/news/?category=technology&sentiment=positive&page=1&page_size=20
    
    Query Parameters:
    - category: Filter by category (technology, business, sports, etc.)
    - sentiment: Filter by sentiment (positive, negative, neutral)
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    - search: Search in title and description
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - sort_by: Sort field (published_at, view_count, like_count) - default: published_at
    """
    try:
        # Get query parameters
        category = request.GET.get('category')
        sentiment = request.GET.get('sentiment')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search = request.GET.get('search')
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        sort_by = request.GET.get('sort_by', 'published_at')
        
        # Build MongoDB query
        filters = {}
        
        if category:
            filters['category'] = category
        
        if sentiment:
            filters['sentiment'] = sentiment
        
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter['$gte'] = datetime.fromisoformat(date_from)
                if date_to:
                    date_filter['$lte'] = datetime.fromisoformat(date_to)
            filters['published_at'] = date_filter
        
        if search:
            filters['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Sort order
        sort_order = -1  # Descending by default
        
        # Get articles
        articles = NewsArticle.get_all(
            filters=filters,
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get total count for pagination
        total_count = NewsArticle.count(filters=filters)
        
        # Add user interaction flags if authenticated
        if request.user.is_authenticated:
            for article in articles:
                article['is_liked'] = ArticleLike.is_liked(request.user.id, article['_id'])
                article['is_saved'] = ArticleSave.is_saved(request.user.id, article['_id'])
        
        # Serialize
        serializer = NewsArticleSerializer(articles, many=True)
        
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_detail(request, article_id):
    """
    Get single news article by ID
    GET /api/news/<article_id>/
    """
    try:
        article = NewsArticle.get_by_id(article_id)
        
        if not article:
            return Response(
                {'error': 'Article not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Track view if user is authenticated
        if request.user.is_authenticated:
            ArticleView.create(request.user.id, article_id)
            NewsArticle.increment_view_count(article_id)
            
            # Add interaction flags
            article['is_liked'] = ArticleLike.is_liked(request.user.id, article_id)
            article['is_saved'] = ArticleSave.is_saved(request.user.id, article_id)
        
        serializer = NewsArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fetch_latest_news(request):
    """
    Manually trigger news fetching (for testing or admin use)
    POST /api/news/fetch/
    Body: { "category": "technology" } (optional)
    """
    try:
        category = request.data.get('category')
        
        aggregator = NewsAggregator()
        saved_count = aggregator.fetch_all_news(category=category)
        
        return Response({
            'message': f'Successfully fetched and saved {saved_count} new articles',
            'saved_count': saved_count
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, article_id):
    """
    Like/unlike an article
    POST /api/news/<article_id>/like/
    """
    try:
        is_liked = ArticleLike.toggle(request.user.id, article_id)
        
        return Response({
            'liked': is_liked,
            'message': 'Article liked' if is_liked else 'Article unliked'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error toggling like: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_save(request, article_id):
    """
    Save/unsave an article
    POST /api/news/<article_id>/save/
    """
    try:
        is_saved = ArticleSave.toggle(request.user.id, article_id)
        
        return Response({
            'saved': is_saved,
            'message': 'Article saved' if is_saved else 'Article unsaved'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error toggling save: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_articles(request):
    """
    Get user's saved articles
    GET /api/news/saved/?page=1&page_size=20
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        skip = (page - 1) * page_size
        
        articles = ArticleSave.get_saved_articles(request.user.id, skip=skip, limit=page_size)
        
        # Add interaction flags
        for article in articles:
            article['is_liked'] = ArticleLike.is_liked(request.user.id, article['_id'])
            article['is_saved'] = True  # All are saved by definition
        
        serializer = NewsArticleSerializer(articles, many=True)
        
        return Response({
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching saved articles: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Get available news categories
    GET /api/news/categories/
    """
    categories = [
        {'value': 'general', 'label': 'General'},
        {'value': 'business', 'label': 'Business'},
        {'value': 'entertainment', 'label': 'Entertainment'},
        {'value': 'health', 'label': 'Health'},
        {'value': 'science', 'label': 'Science'},
        {'value': 'sports', 'label': 'Sports'},
        {'value': 'technology', 'label': 'Technology'},
        {'value': 'politics', 'label': 'Politics'},
        {'value': 'education', 'label': 'Education'},
        {'value': 'lifestyle', 'label': 'Lifestyle'},
    ]
    
    return Response({'categories': categories}, status=status.HTTP_200_OK)
