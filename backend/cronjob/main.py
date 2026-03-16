"""
Scheduled Task Framework Entry
Use APScheduler to manage all scheduled tasks
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from backend.cronjob.email_recommendation import email_recommendation_handler
from backend.cronjob.identify_stars import identify_stars_handler

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

        self.add_job(
            func=email_recommendation_handler,
            trigger=CronTrigger(hour=18, minute=0),
            job_id='email_recommendation_job',
            name='Email Recommendation Task',
            replace_existing=True
        )

        # Additional tasks can be added here, e.g.:
        # self.add_job(
        #     func=other_task,
        #     trigger=IntervalTrigger(minutes=1),
        #     job_id='other_task_job',
        #     name='Other Task',
        #     replace_existing=True
        # )

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
