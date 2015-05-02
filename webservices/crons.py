import models
from datetime import date, timedelta

# This should run every Sunday at midnight
def cleanup_sessions():
    print("Running cron to expire sessions..")
    expire_dt = date.today() - timedelta(days=14)
    sessions_to_clean = models.Session.objects.filter(last_login__lt=expire_dt)
    sessions_to_clean.delete()
    print("Done.")