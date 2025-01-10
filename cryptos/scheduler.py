from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Define the task function
def my_scheduled_task():
    print("Scheduled task is running!")

# Initialize and start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        my_scheduled_task,
        trigger=IntervalTrigger(seconds=10),  # Adjust interval as needed
        id="my_scheduled_task",  # Unique ID for the task
        replace_existing=True,  # Prevent duplicate tasks
    )
    scheduler.start()
    print("Scheduler started")
