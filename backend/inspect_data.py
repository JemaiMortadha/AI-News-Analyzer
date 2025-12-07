import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import NewsArticle

articles = list(NewsArticle.get_collection().find({}, {'sentiment': 1, 'title': 1}).limit(5))
print("Found articles:", len(articles))
for article in articles:
    print(f"Title: {article.get('title')[:30]}... | Sentiment: {article.get('sentiment')}")
