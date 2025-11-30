"""
News Fetching Service
Aggregates news from 4 different APIs:
1. NewsAPI.org - 100 requests/day
2. NewsData.io - 200 requests/day
3. GNews.io - 100 requests/day
4. Currents API - 600 requests/month (~20/day)

Total: ~420 requests/day
"""

import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import NewsArticle
from .dl_model import get_analyzer
import logging

logger = logging.getLogger(__name__)


class NewsAPIFetcher:
    """
    NewsAPI.org fetcher
    Free tier: 100 requests/day, articles have 24h delay
    """
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_top_headlines(self, category=None, country='us', page_size=20):
        """Fetch top headlines"""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        url = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'country': country,
            'pageSize': page_size
        }
        
        if category:
            params['category'] = category
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._parse_articles(data.get('articles', []))
            return []
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    def _parse_articles(self, articles):
        """Parse NewsAPI response to standardized format"""
        parsed = []
        for article in articles:
            parsed.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'content': article.get('content'),
                'url': article.get('url'),
                'image_url': article.get('urlToImage'),
                'source': article.get('source', {}).get('name', 'NewsAPI'),
                'author': article.get('author'),
                'published_at': self._parse_date(article.get('publishedAt')),
                'category': 'general',
                'api_source': 'newsapi'
            })
        return parsed
    
    def _parse_date(self, date_str):
        """Parse ISO 8601 date"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


class NewsDataFetcher:
    """
    NewsData.io fetcher
    Free tier: 200 requests/day
    """
    def __init__(self):
        self.api_key = settings.NEWSDATA_KEY
        self.base_url = "https://newsdata.io/api/1"
        
    def fetch_latest_news(self, category=None, language='en', size=10):
        """Fetch latest news"""
        if not self.api_key:
            logger.warning("NewsData key not configured")
            return []
        
        url = f"{self.base_url}/news"
        params = {
            'apikey': self.api_key,
            'language': language,
            'size': size
        }
        
        if category:
            params['category'] = category
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return self._parse_articles(data.get('results', []))
            return []
        except Exception as e:
            logger.error(f"NewsData error: {e}")
            return []
    
    def _parse_articles(self, articles):
        """Parse NewsData response"""
        parsed = []
        for article in articles:
            parsed.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'content': article.get('content'),
                'url': article.get('link'),
                'image_url': article.get('image_url'),
                'source': article.get('source_id', 'NewsData'),
                'author': article.get('creator', [None])[0] if article.get('creator') else None,
                'published_at': self._parse_date(article.get('pubDate')),
                'category': article.get('category', ['general'])[0] if article.get('category') else 'general',
                'api_source': 'newsdata'
            })
        return parsed
    
    def _parse_date(self, date_str):
        """Parse date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


class GNewsFetcher:
    """
    GNews.io fetcher  
    Free tier: 100 requests/day, 10 articles per request
    """
    def __init__(self):
        self.api_key = settings.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4"
        
    def fetch_top_headlines(self, category=None, lang='en', max_results=10):
        """Fetch top headlines"""
        if not self.api_key:
            logger.warning("GNews key not configured")
            return []
        
        url = f"{self.base_url}/top-headlines"
        params = {
            'apikey': self.api_key,
            'lang': lang,
            'max': max_results
        }
        
        if category:
            params['category'] = category
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_articles(data.get('articles', []))
        except Exception as e:
            logger.error(f"GNews error: {e}")
            return []
    
    def _parse_articles(self, articles):
        """Parse GNews response"""
        parsed = []
        for article in articles:
            parsed.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'content': article.get('content'),
                'url': article.get('url'),
                'image_url': article.get('image'),
                'source': article.get('source', {}).get('name', 'GNews'),
                'author': None,  # GNews doesn't provide author
                'published_at': self._parse_date(article.get('publishedAt')),
                'category': 'general',
                'api_source': 'gnews'
            })
        return parsed
    
    def _parse_date(self, date_str):
        """Parse ISO 8601 date"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


class CurrentsAPIFetcher:
    """
    Currents API fetcher
    Free tier: 600 requests/month (~20/day)
    """
    def __init__(self):
        self.api_key = settings.CURRENTS_API_KEY
        self.base_url = "https://api.currentsapi.services/v1"
        
    def fetch_latest_news(self, category=None, language='en'):
        """Fetch latest news"""
        if not self.api_key:
            logger.warning("Currents API key not configured")
            return []
        
        url = f"{self.base_url}/latest-news"
        params = {
            'apiKey': self.api_key,
            'language': language
        }
        
        if category:
            params['category'] = category
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._parse_articles(data.get('news', []))
            return []
        except Exception as e:
            logger.error(f"Currents API error: {e}")
            return []
    
    def _parse_articles(self, articles):
        """Parse Currents API response"""
        parsed = []
        for article in articles:
            parsed.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'content': article.get('description'),  # Currents doesn't provide full content
                'url': article.get('url'),
                'image_url': article.get('image'),
                'source': 'Currents',
                'author': article.get('author'),
                'published_at': self._parse_date(article.get('published')),
                'category': article.get('category', ['general'])[0] if article.get('category') else 'general',
                'api_source': 'currents'
            })
        return parsed
    
    def _parse_date(self, date_str):
        """Parse date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


class NewsAggregator:
    """
    Aggregates news from all sources with duplicate detection
    """
    def __init__(self):
        self.newsapi = NewsAPIFetcher()
        self.newsdata = NewsDataFetcher()
        self.gnews = GNewsFetcher()
        self.currents = CurrentsAPIFetcher()
        self.analyzer = None
        
    def fetch_all_news(self, category=None):
        """
        Fetch news from all APIs
        Returns: Number of new articles added
        """
        all_articles = []
        
        # Fetch from all sources
        logger.info("Fetching from NewsAPI...")
        all_articles.extend(self.newsapi.fetch_top_headlines(category=category, page_size=20))
        
        logger.info("Fetching from NewsData...")
        all_articles.extend(self.newsdata.fetch_latest_news(category=category, size=10))
        
        logger.info("Fetching from GNews...")
        all_articles.extend(self.gnews.fetch_top_headlines(category=category, max_results=10))
        
        logger.info("Fetching from Currents API...")
        all_articles.extend(self.currents.fetch_latest_news(category=category))
        
        logger.info(f"Fetched {len(all_articles)} total articles from all sources")
        
        # Remove duplicates and save to database
        saved_count = self._save_unique_articles(all_articles)
        
        logger.info(f"Saved {saved_count} new unique articles to database")
        return saved_count
    
    def _save_unique_articles(self, articles):
        """
        Save articles to MongoDB, avoiding duplicates
        Duplicate detection: same URL
        """
        saved_count = 0
        
        for article_data in articles:
            # Skip if no URL (required field)
            if not article_data.get('url'):
                continue
            
            # Check if article already exists by URL
            existing = NewsArticle.get_collection().find_one({'url': article_data['url']})
            if existing:
                continue
            
            # Analyze sentiment (Text + Image)
            sentiment_data = self._analyze_multimodal(article_data)
            
            # Create article with sentiment
            article = NewsArticle.create(
                title=article_data.get('title'),
                description=article_data.get('description'),
                content=article_data.get('content'),
                url=article_data['url'],
                image_url=article_data.get('image_url'),
                source=article_data.get('source', 'Unknown'),
                author=article_data.get('author'),
                category=self._normalize_category(article_data.get('category', 'general')),
                sentiment=sentiment_data.get('sentiment'),
                sentiment_confidence=sentiment_data.get('confidence'),
                published_at=article_data.get('published_at', datetime.utcnow())
            )
            
            if article:
                saved_count += 1
        
        return saved_count
    
    def _analyze_multimodal(self, article_data):
        """
        Perform multi-modal sentiment analysis (Text + Image)
        Logic:
        - Text weight: 2
        - Image weight: 1
        - Conflict resolution rules applied
        """
        # 1. Text Analysis
        text_result = self._analyze_text(article_data.get('title', ''), article_data.get('description', ''))
        
        # 2. Image Analysis
        image_result = {'sentiment': 'neutral', 'confidence': 0.0}
        if article_data.get('image_url'):
            image_result = self._analyze_image(article_data['image_url'])
            
        # 3. Combine Results
        return self._combine_sentiments(text_result, image_result)

    def _analyze_text(self, title, description):
        """Analyze sentiment of article text"""
        try:
            # Lazy load analyzer
            if not self.analyzer:
                self.analyzer = get_analyzer()
            
            # Combine title and description
            text = f"{title}. {description}" if description else title
            
            if not text:
                return {'sentiment': 'neutral', 'confidence': 0.0}
            
            # Get sentiment
            result = self.analyzer.predict(text)
            return result
        except Exception as e:
            logger.error(f"Text sentiment analysis error: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0}

    def _analyze_image(self, image_url):
        """Analyze sentiment of article image"""
        try:
            from .image_model import get_image_analyzer
            analyzer = get_image_analyzer()
            return analyzer.predict(image_url)
        except Exception as e:
            logger.error(f"Image sentiment analysis error: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0}

    def _combine_sentiments(self, text_res, img_res):
        """
        Combine text and image sentiment with specific rules:
        - Text has 2 votes, Image has 1 vote
        - P=Positive, N=Negative, Ne=Neutral
        
        Rules:
        1. P vs N (Conflict): Weighted average of confidence
        2. Ne vs P/N: If P/N confidence > 40%, choose P/N. Else Neutral.
        3. Ne vs Ne: Neutral
        """
        t_sent = text_res['sentiment']
        t_conf = text_res['confidence']
        i_sent = img_res['sentiment']
        i_conf = img_res['confidence']
        
        # Map to numerical values for calculation (P=1, N=-1, Ne=0)
        val_map = {'positive': 1, 'negative': -1, 'neutral': 0}
        t_val = val_map.get(t_sent, 0)
        i_val = val_map.get(i_sent, 0)
        
        # Rule 3: Both Neutral
        if t_sent == 'neutral' and i_sent == 'neutral':
            return {'sentiment': 'neutral', 'confidence': (t_conf + i_conf) / 2}
            
        # Rule 2: One Neutral, One Non-Neutral
        if t_sent == 'neutral' or i_sent == 'neutral':
            non_neutral_res = text_res if t_sent != 'neutral' else img_res
            if non_neutral_res['confidence'] > 0.40:
                return non_neutral_res
            else:
                return {'sentiment': 'neutral', 'confidence': non_neutral_res['confidence']}
                
        # Rule 1: Conflict (P vs N) or Agreement (P vs P, N vs N)
        # Weighted Score = (2 * Text_Val * Text_Conf + 1 * Image_Val * Image_Conf) / 3
        weighted_score = (2 * t_val * t_conf + 1 * i_val * i_conf) / 3
        
        final_sentiment = 'neutral'
        if weighted_score > 0.1: # Threshold for positive
            final_sentiment = 'positive'
        elif weighted_score < -0.1: # Threshold for negative
            final_sentiment = 'negative'
            
        return {'sentiment': final_sentiment, 'confidence': abs(weighted_score)}

    def _normalize_category(self, category):
        """Normalize category names across different APIs"""
        category_map = {
            # NewsAPI categories
            'business': 'business',
            'entertainment': 'entertainment',
            'general': 'general',
            'health': 'health',
            'science': 'science',
            'sports': 'sports',
            'technology': 'technology',
            
            # NewsData categories
            'top': 'general',
            'world': 'general',
            'politics': 'politics',
            'crime': 'general',
            'domestic': 'general',
            'education': 'education',
            'environment': 'science',
            'food': 'lifestyle',
            'lifestyle': 'lifestyle',
            'tourism': 'lifestyle',
            
            # GNews categories
            'nation': 'general',
            'world': 'general',
            
            # Currents API categories
            'regional': 'general',
            'programming': 'technology',
            'academia': 'education'
        }
        
        return category_map.get(category.lower() if category else 'general', 'general')
    
    def fetch_by_category(self, category):
        """Fetch news for specific category"""
        return self.fetch_all_news(category=category)
