from django.urls import path
from . import views, auth_views, news_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication
    path('auth/register/', auth_views.register_user, name='register'),
    path('auth/login/', auth_views.login_user, name='login'),
    path('auth/logout/', auth_views.logout_user, name='logout'),
    path('auth/profile/', auth_views.user_profile, name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # News
    path('news/', news_views.get_news_list, name='news-list'),
    path('news/fetch/', news_views.fetch_latest_news, name='news-fetch'),
    path('news/saved/', news_views.get_saved_articles, name='news-saved'),
    path('news/categories/', news_views.get_categories, name='news-categories'),
    path('news/<str:article_id>/', news_views.get_news_detail, name='news-detail'),
    path('news/<str:article_id>/like/', news_views.toggle_like, name='news-like'),
    path('news/<str:article_id>/save/', news_views.toggle_save, name='news-save'),
    
    # Sentiment Analysis (legacy)
    path('analyze/', views.analyze_sentiment, name='analyze'),
    path('analyze-image/', views.analyze_image_sentiment, name='analyze-image'),
    path('articles/', views.get_articles, name='articles'),
]