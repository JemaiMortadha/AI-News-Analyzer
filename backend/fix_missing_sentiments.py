import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import NewsArticle
from analyzer.news_fetcher import NewsAggregator

def fix_sentiments():
    aggregator = NewsAggregator()
    collection = NewsArticle.get_collection()
    
    # Find articles with missing sentiment
    articles = list(collection.find({
        '$or': [
            {'sentiment': None},
            {'sentiment': {'$exists': False}}
        ]
    }))
    
    print(f"Found {len(articles)} articles with missing sentiment.")
    
    updated_count = 0
    for article in articles:
        print(f"Analyzing: {article.get('title')[:50]}...")
        
        # Re-construct article data for analysis
        article_data = {
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('url'),
            'image_url': article.get('image_url')
        }
        
        try:
            sentiment_data = aggregator._analyze_multimodal(article_data)
            
            # Update article
            collection.update_one(
                {'_id': article['_id']},
                {'$set': {
                    'sentiment': sentiment_data['sentiment'],
                    'sentiment_confidence': sentiment_data['confidence']
                }}
            )
            updated_count += 1
            print(f"  -> Set to: {sentiment_data['sentiment']}")
        except Exception as e:
            print(f"  -> Error: {e}")
            
    print(f"Finished! Updated {updated_count} articles.")

if __name__ == '__main__':
    fix_sentiments()
