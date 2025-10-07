from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .ml_model import get_analyzer
from .serializers import AnalyzeRequestSerializer, ArticleSerializer

@api_view(['POST'])
def analyze_sentiment(request):
    """
    Analyze sentiment of provided text
    POST /api/analyze/
    Body: { "text": "article content" }
    """
    serializer = AnalyzeRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    text = serializer.validated_data['text']
    
    try:
        # Get sentiment analyzer
        analyzer = get_analyzer()
        
        # Predict sentiment
        result = analyzer.predict(text)
        
        # Save to MongoDB
        Article.create(
            text=text,
            sentiment=result['sentiment'],
            confidence=result['confidence']
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_articles(request):
    """
    Get recent analyzed articles
    GET /api/articles/
    """
    try:
        articles = Article.get_recent(limit=10)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )