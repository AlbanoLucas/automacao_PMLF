from imports import *

# locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

# Obtém o nome do dia da semana
dia = datetime.today().strftime("%A")
print(dia)