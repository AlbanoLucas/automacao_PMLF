from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()