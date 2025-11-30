from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'
    
    def ready(self):
        """Start background scheduler when Django starts"""
        import os
        # Only start scheduler in main process (not in reloader)
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()
