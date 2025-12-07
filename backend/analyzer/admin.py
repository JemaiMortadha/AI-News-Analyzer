from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.template.response import TemplateResponse
from .models import User, NewsArticle, FetchLog
from .news_fetcher import NewsAggregator
from datetime import datetime


# Enhanced User Admin with full permissions
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = ('groups', 'user_permissions',)


# Re-register Group to make it available
admin.site.unregister(Group)
admin.site.register(Group)


# Custom admin views for MongoDB data
def news_articles_view(request):
    """Display news articles from MongoDB"""
    # Get filter parameters
    category = request.GET.get('category', '')
    sentiment = request.GET.get('sentiment', '')
    search = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = 50
    
    # Build filters
    filters = {}
    if category:
        filters['category'] = category
    if sentiment:
        filters['sentiment'] = sentiment
    if search:
        filters['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    # Get articles
    skip = (page - 1) * per_page
    articles = NewsArticle.get_all(filters=filters, limit=per_page, skip=skip)
    
    # Get total count
    total_count = NewsArticle.get_collection().count_documents(filters)
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    # Get unique categories for filters
    try:
        categories = NewsArticle.get_collection().distinct('category')
    except:
        categories = []
    
    sentiments = ['Positive', 'Neutral', 'Negative']
    
    context = {
        **admin.site.each_context(request),
        'title': 'News Articles',
        'articles': articles,
        'categories': sorted(categories) if categories else [],
        'sentiments': sentiments,
        'selected_category': category,
        'selected_sentiment': sentiment,
        'search_query': search,
        'page': page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_previous': page > 1,
        'has_next': page < total_pages,
    }
    
    return TemplateResponse(request, 'admin/news_articles.html', context)


def fetch_news_view(request):
    """Manually trigger news fetching"""
    if request.method == 'POST':
        try:
            start_time = datetime.utcnow()
            aggregator = NewsAggregator()
            total_articles = aggregator.fetch_all_news()
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Log the fetch
            FetchLog.create(
                articles_count=total_articles,
                status='success',
                duration=duration
            )
            
            messages.success(request, f'✓ Successfully fetched {total_articles} articles in {duration:.2f} seconds!')
        except Exception as e:
            FetchLog.create(
                articles_count=0,
                status='error',
                error_message=str(e)
            )
            messages.error(request, f'✗ Error fetching news: {str(e)}')
    
    return redirect('/admin/news-articles/')


# Add custom URLs to admin
from django.contrib.admin import AdminSite

original_get_urls = AdminSite.get_urls

def custom_get_urls(self):
    urls = original_get_urls(self)
    from django.urls import path
    custom_urls = [
        path('news-articles/', news_articles_view, name='news_articles'),
        path('news-articles/fetch/', fetch_news_view, name='fetch_news'),
    ]
    return custom_urls + urls

AdminSite.get_urls = custom_get_urls


# Customize admin site headers
admin.site.site_header = 'AI News Analyzer Admin'
admin.site.site_title = 'AI News Admin'
admin.site.index_title = 'Welcome to AI News Analyzer Administration'
