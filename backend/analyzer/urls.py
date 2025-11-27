from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_sentiment, name='analyze'),
    path('analyze-image/', views.analyze_image_sentiment, name='analyze-image'),
    path('articles/', views.get_articles, name='articles'),
]