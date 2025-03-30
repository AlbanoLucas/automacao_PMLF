from celery import Celery

# Configure o Celery com o broker Redis
app = Celery('diario', broker='redis://localhost:6379/0')

# Configuração adicional
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
)
app.conf.update(
    worker_pool='prefork',  # Muda o pool para 'prefork', que pode ser mais adequado para sistemas Windows
)
