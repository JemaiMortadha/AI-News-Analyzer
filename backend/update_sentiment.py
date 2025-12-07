import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import NewsArticle

# Update one article
article = NewsArticle.get_collection().find_one()
if article:
    print(f"Updating article: {article.get('title')}")
    NewsArticle.get_collection().update_one(
        {'_id': article['_id']},
        {'$set': {'sentiment': 'Positive'}}
    )
    print("Updated sentiment to 'Positive'")
else:
    print("No articles found")
