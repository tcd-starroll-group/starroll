"""
Scheduled Task Framework Entry
Use APScheduler to manage all scheduled tasks
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from backend.cronjob.identify_stars import identify_stars_handler
from backend.cronjob.precompute_stargazing import precompute_stargazing_handler
from backend.cronjob.update_user_stargazing_profile import update_user_stargazing_profile_handler
from backend.cronjob.send_stargazing_recommendation_email import send_stargazing_recommendation_email_handler

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CronJobScheduler:
    """Scheduler for scheduled tasks"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self._register_jobs()

    def _register_jobs(self):
        """Register all scheduled tasks"""
        # Example: Execute identify_satrs every 5 seconds
        self.add_job(
            func=identify_stars_handler,
            trigger=IntervalTrigger(seconds=5),
            job_id='identify_satrs_job',
            name='Identify Stars Task',
            replace_existing=True
        )

        # Precompute stargazing recommendations for popular dark-sky locations every 3 hours
        self.add_job(
            func=precompute_stargazing_handler,
            trigger=IntervalTrigger(hours=3),
            job_id='precompute_stargazing_job',
            name='Precompute Stargazing Recommendations',
            replace_existing=True
        )

        # Update user stargazing profiles from observation history every 6 hours
        self.add_job(
            func=update_user_stargazing_profile_handler,
            trigger=IntervalTrigger(hours=6),
            job_id='update_user_stargazing_profile_job',
            name='Update User Stargazing Profiles',
            replace_existing=True
        )

        # Send daily stargazing recommendation emails at 18:00 every day
        # (early evening so users can plan for the night)
        self.add_job(
            func=send_stargazing_recommendation_email_handler,
            trigger=CronTrigger(hour=18, minute=0),
            job_id='send_stargazing_recommendation_email_job',
            name='Send Daily Stargazing Recommendation Emails',
            replace_existing=True
        )

    def add_job(self, func, trigger, job_id, name, replace_existing=True):
        """
        General method to add scheduled tasks

        Args:
            func: Function to execute
            trigger: Trigger (e.g., IntervalTrigger)
            job_id: Unique identifier for the task
            name: Task name
            replace_existing: Whether to replace an existing task with the same ID
        """
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=replace_existing,
            misfire_grace_time=10
        )
        logger.info(f'Task registered: {name} (ID: {job_id})')

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info('Scheduler started')

    def shutdown(self):
        """Shut down the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info('Scheduler shut down')

    def pause_job(self, job_id):
        """Pause a specific task"""
        self.scheduler.pause_job(job_id)
        logger.info(f'Task paused: {job_id}')

    def resume_job(self, job_id):
        """Resume a specific task"""
        self.scheduler.resume_job(job_id)
        logger.info(f'Task resumed: {job_id}')

    def list_jobs(self):
        """List all tasks"""
        return self.scheduler.get_jobs()


# Global scheduler instance
_scheduler = None


def get_scheduler():
    """Get the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = CronJobScheduler()
    return _scheduler


def main():
    """Main entry point"""
    try:
        scheduler = get_scheduler()
        scheduler.start()

        # Print registered tasks
        logger.info('Registered scheduled tasks:')
        for job in scheduler.list_jobs():
            logger.info(
                f'  - {job.name} (ID: {job.id}, Trigger: {job.trigger})')

        # Keep the main thread running
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info('Received stop signal')
        scheduler = get_scheduler()
        scheduler.shutdown()
    except Exception as e:
        logger.error(f'Scheduled task framework error: {e}', exc_info=True)
        scheduler = get_scheduler()
        scheduler.shutdown()


if __name__ == '__main__':
    main()
