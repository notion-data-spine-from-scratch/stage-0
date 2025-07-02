from .celery import celery_app, consume_and_index

if __name__ == "__main__":
    consume_and_index.delay()
    celery_app.worker_main(["worker", "--loglevel=info"])
