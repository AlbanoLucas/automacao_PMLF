from celery import Celery
from celery.schedules import crontab


# Configure o Celery com o broker Redis
app = Celery('diario', broker='redis://localhost:6379/0')

# Configuração adicional
app.conf.update(
    result_backend='redis://localhost:6379/0',  # Redis como backend para resultados
    task_serializer='json',  # Formato de serialização das tarefas
    timezone='America/Sao_Paulo',  # Definindo o fuso horário para o Brasil
    enable_utc=True,  # Utilizar UTC para todas as tarefas
)

# Adicionalmente, se for necessário configurar o Celery Beat, faça assim:
app.conf.beat_schedule = {
    'executar-tarefa': {
        'task': 'tasks.run_my_script',  # Nome da tarefa a ser agendada
        'schedule': crontab(hour=8, minute=30, day_of_week='1-5'),  # Segunda a sexta às 8:30
    },
}
