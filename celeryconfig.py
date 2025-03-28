from celery.schedules import crontab

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

timezone = 'America/Sao_Paulo'

# Segunda a sexta às 08:30
beat_schedule = {
    'run_task_every_weekday': {
        'task': 'tasks.run_my_script',
        'schedule': crontab(hour=8, minute=30, day_of_week='1-5'),  
    },
}
