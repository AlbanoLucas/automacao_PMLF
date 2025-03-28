from celery import Celery
from diario_ofc import run_full_process  # Substitua pelo nome correto do seu script principal

app = Celery('tasks')
app.config_from_object('celeryconfig')

@app.task
def run_my_script():
    run_full_process()  # Essa função deve executar todo o fluxo do seu código
