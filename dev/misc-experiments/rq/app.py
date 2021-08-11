
# https://www.twilio.com/blog/first-task-rq-redis-python

from datetime import datetime, timedelta
import time
from redis import Redis
from rq import Queue
import tasks

queue = Queue(connection=Redis())

def queue_tasks():
    queue.enqueue(tasks.print_task, 5)
    queue.enqueue_in(timedelta(seconds=10), tasks.print_numbers, 5)

def main():
    queue_tasks()

if __name__ == "__main__":
    main()
