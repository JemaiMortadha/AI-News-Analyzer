import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import NewsArticle, ArticleView

def check_views():
    print("--- Checking NewsArticle view_counts ---")
    # Get articles with view_count > 0
    articles = NewsArticle.get_all(sort_by='view_count', sort_order=-1, limit=5)
    
    count_with_views = 0
    for a in articles:
        views = a.get('view_count', 0)
        if views > 0:
            print(f"Title: {a.get('title')[:50]}... | Views: {views}")
            count_with_views += 1
    
    if count_with_views == 0:
        print("No articles found with view_count > 0")

    print("\n--- Checking ArticleView collection ---")
    # Check raw view logs
    view_logs_count = ArticleView.get_collection().count_documents({})
    print(f"Total entries in ArticleView collection: {view_logs_count}")

if __name__ == "__main__":
    check_views()
