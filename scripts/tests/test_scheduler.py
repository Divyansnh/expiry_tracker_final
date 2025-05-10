from app import create_app
from app.core.extensions import scheduler
from datetime import datetime, timedelta

def test_scheduler():
    app = create_app()
    with app.app_context():
        # Get all scheduled jobs
        jobs = scheduler.get_jobs()
        print("\nScheduled Jobs:")
        for job in jobs:
            print(f"Job ID: {job.id}")
            print(f"Next run time: {job.next_run_time}")
            print(f"Trigger: {job.trigger}")
            print("---")

if __name__ == '__main__':
    test_scheduler() 