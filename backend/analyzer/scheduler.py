"""
Background task scheduler for automatic news fetching
Uses APScheduler to fetch news every 6 hours
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from .models import User, UserProfile
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def fetch_news_task():
    """Background task to fetch news from all APIs"""
    try:
        from .news_fetcher import NewsAggregator
        
        logger.info("Starting scheduled news fetch...")
        aggregator = NewsAggregator()
        count = aggregator.fetch_all_news()
        logger.info(f"Scheduled fetch completed: {count} new articles saved")
    except Exception as e:
        logger.error(f"Error in scheduled news fetch: {e}")


def send_daily_digests_task():
    """Background task to send daily digests to all subscribed users"""
    try:
        from .email_service import EmailService
        
        logger.info("Starting daily digest sending task...")
        email_service = EmailService()
        
        # Get all users
        users = User.objects.filter(is_active=True)
        sent_count = 0
        
        for user in users:
            # Check profile preferences
            profile = UserProfile.get_by_user_id(user.id)
            if profile and profile.get('notification_enabled', True):
                # Check frequency (daily vs weekly) - simplified for now to just daily
                if profile.get('notification_frequency', 'daily') == 'daily':
                    if email_service.send_daily_digest(user.id):
                        sent_count += 1
        
        logger.info(f"Daily digests sent to {sent_count} users")
        
    except Exception as e:
        logger.error(f"Error in daily digest task: {e}")


def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Fetch news every 6 hours (at 00:00, 06:00, 12:00, 18:00)
        scheduler.add_job(
            fetch_news_task,
            trigger=CronTrigger(hour='0,6,12,18', minute=0),
            id='fetch_news',
            name='Fetch news from all APIs',
            replace_existing=True
        )
        
        # Send daily digests at 8:00 AM
        scheduler.add_job(
            send_daily_digests_task,
            trigger=CronTrigger(hour=8, minute=0),
            id='send_digests',
            name='Send daily email digests',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started (News: 6h, Emails: 8am)")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
