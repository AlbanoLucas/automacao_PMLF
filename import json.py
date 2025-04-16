import json

# Nome do arquivo JSON de entrada
arquivo_json = "resultados_projeto_engenharia.json"

# Nome do arquivo TXT de saída
arquivo_txt = "resultados_projeto_engenharia.txt"

# Função recursiva para formatar qualquer estrutura JSON
def formatar_json_para_txt(dados, nivel=0):
    texto = ""
    prefixo = "  " * nivel
    if isinstance(dados, dict):
        for chave, valor in dados.items():
            texto += f"{prefixo}{chave}:\n{formatar_json_para_txt(valor, nivel + 1)}"
    elif isinstance(dados, list):
        for i, item in enumerate(dados):
            texto += f"{prefixo}- Item {i + 1}:\n{formatar_json_para_txt(item, nivel + 1)}"
    else:
        texto += f"{prefixo}{dados}\n"
    return texto

# Lê o JSON e salva como TXT
with open(arquivo_json, "r", encoding="utf-8") as f:
    dados = json.load(f)

texto_formatado = formatar_json_para_txt(dados)

with open(arquivo_txt, "w", encoding="utf-8") as f:
    f.write(texto_formatado)

print(f"Arquivo TXT gerado: {arquivo_txt}")
