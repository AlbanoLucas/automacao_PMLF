from celery import Celery
from celery.schedules import crontab
from tasks import run_my_script

app = Celery('minha_aplicacao', broker='redis://localhost:6379/0')

# Configuração do Celery Beat para agendar a execução de tarefas
app.conf.beat_schedule = {
    'executar-por-agendamento': {
        'task': 'tasks.run_my_script',  # Nome da tarefa que você quer agendar
        # 'schedule': crontab(hour=8, minute=30, day_of_week='1-5'),  # Segunda a sexta às 8:30
        'schedule': crontab(minute='*/15'),  # A cada 15 minutos
    },
}
