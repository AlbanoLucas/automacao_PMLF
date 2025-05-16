import pandas as pd
from datetime import datetime

def calcular_idade(data_nascimento):
    """Calcula a idade a partir de um número inteiro de data do Excel."""
    try:
        # Converter o número inteiro para uma data
        # nascimento = datetime.strptime(data_nascimento, "%d/%m/%Y")
        nascimento = pd.to_datetime(data_nascimento, origin='1899-12-30', unit='D')
        hoje = datetime.today()
        idade = hoje.year - nascimento.year
        # Verificar se já fez aniversário no ano atual
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return idade
    except Exception as e:
        print(f"Erro ao calcular idade: {data_nascimento} -> {e}")
        return None

def obter_faixa_etaria(idade):
    """Retorna o índice da faixa etária correspondente."""
    for faixa, intervalo in relacao_planos.items():
        if idade in intervalo:
            return faixa
    return None

def registrar_alteracao(log_file, mensagem):
    """Registra a alteração no arquivo de log."""
    with open(log_file, "a") as log:
        log.write(mensagem + "\n")
    print(mensagem)

# Planos disponíveis com seus valores
planos = [
    {"id": 5253, "1": 174.38, "2": 263.05, "3": 429.86, "4": 1028.12},
    {"id": 5257, "1": 215.75, "2": 326.57, "3": 535.06, "4": 1282.9},
    {"id": 5249, "1": 226.7, "2": 341.97, "3": 558.81, "4": 1336.55},
    {"id": 5251, "1": 317.37, "2": 478.76, "3": 782.34, "4": 1871.17}
]

# Faixa etária por plano
relacao_planos = {
    1: range(0, 19),    # Idade de 0 a 18
    2: range(19, 44),   # Idade de 19 a 43
    3: range(44, 59),   # Idade de 44 a 58
    4: range(59, 150)   # Idade de 59 a 149
}

hoje = datetime.today().strftime("%d-%m-%Y")
# 📝 Arquivo Excel e Log
arquivo_excel = "planilha_consig_plano.xlsx"
log_file = f"log_alteracoes_{hoje}.txt"

# 🧠 Carregar a planilha Excel
df = pd.read_excel(arquivo_excel, header=0)
df = df.fillna('')

# Visualizar as colunas da planilha
print("Colunas da Planilha:", df.columns.tolist())

# Iterar pelas linhas da planilha
for index, linha in df.iterrows():
    # Verificar se a linha está vazia
    if linha.isnull().all():
        continue

    try:
        nome = str(linha["BENEFICIARIO"]).strip()
        nascimento = linha["NASCIMENTO"]
        plano_id = int(float(str(linha["PLANO"]).strip()))

        # Calcular a idade usando o número inteiro da data
        idade = calcular_idade(nascimento)
        if idade is None:
            continue

        # Obter a faixa etária
        faixa = obter_faixa_etaria(idade)

        # Procurar o valor do plano correspondente
        valor_plano = None
        for plano in planos:
            if plano["id"] == plano_id:
                valor_plano = plano.get(str(faixa), "Não encontrado")
                break

        # Comparar os valores e atualizar a planilha se necessário
        alterado = False
        log_mensagem = f"Nome: {nome} - "

        # Comparar idade
        if df.at[index, "IDADE"] != idade:
            log_mensagem += f"[IDADE] {df.at[index, 'IDADE']} -> {idade} | "
            df.at[index, "IDADE"] = idade
            alterado = True

        # # Comparar plano
        # if df.at[index, "PLANO"] != plano_id:
        #     log_mensagem += f"[PLANO] {df.at[index, 'PLANO']} -> {plano_id} | "
        #     df.at[index, "PLANO"] = plano_id
        #     alterado = True

        # Comparar mensalidade
        if df.at[index, "MENSALIDADE"] != valor_plano:
            log_mensagem += f"[MENSALIDADE] {df.at[index, 'MENSALIDADE']} -> {valor_plano} | "
            df.at[index, "MENSALIDADE"] = valor_plano
            alterado = True

        # Registrar no log se houve alteração
        if alterado:
            registrar_alteracao(log_file, log_mensagem)

    except Exception as e:
        print(f"Erro ao processar linha: {linha} -> {e}")
        continue

# 📝 Salvar a planilha atualizada
df.to_excel("planilha_consig_plano_atualizada.xlsx", index=False)
print("Atualização concluída e log gerado.")
