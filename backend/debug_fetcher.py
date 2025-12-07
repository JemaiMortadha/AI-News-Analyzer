import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.news_fetcher import NewsAggregator

aggregator = NewsAggregator()

# Mock article data
article_data = {
    'title': 'Test Article about AI',
    'description': 'Artificial Intelligence is growing rapidly and changing the world in positive ways.',
    'url': 'http://example.com/test',
    'image_url': None
}

print("Testing sentiment analysis...")
try:
    sentiment_data = aggregator._analyze_multimodal(article_data)
    print(f"Sentiment Data: {sentiment_data}")
except Exception as e:
    print(f"Error: {e}")
