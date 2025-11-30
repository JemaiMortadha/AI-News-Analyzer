"""
Email Service using Brevo (formerly Sendinblue)
Handles sending transactional emails and newsletters
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from .models import User, UserProfile, NewsArticle, EmailLog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.sender_email = settings.BREVO_SENDER_EMAIL
        self.sender_name = settings.BREVO_SENDER_NAME
        
        # Configure API key authorization
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = self.api_key
        
        # Create API instance
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

    def send_welcome_email(self, user):
        """Send welcome email to new user"""
        subject = "Welcome to AI News Analyzer!"
        html_content = f"""
        <html>
            <body>
                <h1>Welcome, {user.username}!</h1>
                <p>Thank you for joining AI News Analyzer.</p>
                <p>We're excited to help you stay updated with the latest news, analyzed by AI.</p>
                <p>You can now:</p>
                <ul>
                    <li>Browse aggregated news from multiple sources</li>
                    <li>See AI-powered sentiment analysis</li>
                    <li>Save your favorite articles</li>
                    <li>Customize your news feed</li>
                </ul>
                <br>
                <p>Best regards,</p>
                <p>The AI News Analyzer Team</p>
            </body>
        </html>
        """
        
        return self._send_email(user.email, user.username, subject, html_content)

    def send_daily_digest(self, user_id):
        """Send daily news digest based on user preferences"""
        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.get_by_user_id(user_id)
            
            if not profile or not profile.get('notification_enabled', True):
                return False
            
            # Get user categories
            categories = profile.get('notification_categories', [])
            if not categories:
                categories = profile.get('favorite_categories', [])
            if not categories:
                categories = ['general', 'technology']  # Default
            
            # Fetch recent top articles for these categories
            articles = []
            for category in categories:
                # Get top 3 articles from last 24h with positive sentiment
                recent_articles = NewsArticle.get_all(
                    filters={
                        'category': category,
                        'published_at': {'$gte': datetime.utcnow() - timedelta(hours=24)},
                        # Prefer positive/neutral news for digest
                        'sentiment': {'$in': ['Positive', 'Neutral']}
                    },
                    limit=3,
                    sort_by='sentiment_confidence'
                )
                articles.extend(recent_articles)
            
            if not articles:
                logger.info(f"No articles found for digest for user {user.email}")
                return False
            
            # Deduplicate articles
            unique_articles = {a['url']: a for a in articles}.values()
            
            # Generate HTML content
            articles_html = ""
            for article in unique_articles:
                articles_html += f"""
                <div style="margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                    <h3><a href="{article.get('url')}">{article.get('title')}</a></h3>
                    <p style="color: #666; font-size: 12px;">
                        {article.get('source')} | {article.get('category').title()} | 
                        Sentiment: <strong>{article.get('sentiment')}</strong>
                    </p>
                    <p>{article.get('description') or ''}</p>
                </div>
                """
            
            html_content = f"""
            <html>
                <body>
                    <h1>Your Daily AI News Digest</h1>
                    <p>Here are the top stories for you today based on your preferences:</p>
                    <br>
                    {articles_html}
                    <br>
                    <p><a href="http://localhost:5173">View more on AI News Analyzer</a></p>
                    <p style="font-size: 10px; color: #999;">
                        You received this email because you subscribed to daily digests. 
                        <a href="http://localhost:5173/profile">Manage preferences</a>
                    </p>
                </body>
            </html>
            """
            
            # Send email
            if self._send_email(user.email, user.username, "Your Daily AI News Digest", html_content):
                # Log email
                EmailLog.create(user_id, 'daily_digest', [a['_id'] for a in unique_articles])
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error sending digest to user {user_id}: {e}")
            return False

    def _send_email(self, to_email, to_name, subject, html_content):
        """Internal method to send email via Brevo"""
        if not self.api_key:
            logger.warning("Brevo API key not configured")
            return False
            
        sender = {"name": self.sender_name, "email": self.sender_email}
        to = [{"email": to_email, "name": to_name}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=subject,
            html_content=html_content
        )
        
        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent to {to_email}: {api_response}")
            return True
        except ApiException as e:
            logger.error(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
            return False
