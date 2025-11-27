from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .dl_model import get_analyzer 
from .image_model import get_image_analyzer
from .serializers import AnalyzeRequestSerializer, ArticleSerializer
import os
import tempfile

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

@api_view(['POST'])
def analyze_image_sentiment(request):
    """
    Analyze sentiment of provided image
    POST /api/analyze-image/
    Body: FormData with 'image' file
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    file_ext = os.path.splitext(image_file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response(
            {'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        # Get image sentiment analyzer
        analyzer = get_image_analyzer()
        
        # Predict sentiment
        result = analyzer.predict(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except FileNotFoundError:
        return Response(
            {'error': 'Image model not found. Please train the model first.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        
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