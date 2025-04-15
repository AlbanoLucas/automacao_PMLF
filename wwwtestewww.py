import os
import json
import pdfplumber
from openai import OpenAI

PASTA_PDFS = r"C:\\Users\\aesouza\\Desktop\\projetos_engenharia_ambiental"

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

# Consulta ao LLaMA com prompt técnico
def consultar_llm(texto_pdf):
    try:
        resposta = client.chat.completions.create(
            model="llama3:8b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em projetos de engenharia ambiental. "
                        "Sua tarefa é analisar documentos técnicos e gerar um resumo detalhado e objetivo contendo:\n\n"
                        "- Título e objetivo do projeto\n- Localização\n- Responsáveis técnicos\n"
                        "- Estudos de impacto ambiental\n- Principais medidas mitigadoras\n"
                        "- Licenciamentos mencionados\n- Prazos, cronogramas ou fases\n- Qualquer dado técnico relevante\n\n"
                        "Use linguagem técnica e clara. Não inclua informações genéricas nem apenas datas."
                    )
                },
                {
                    "role": "user",
                    "content": texto_pdf
                }
            ],
            temperature=0.2
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar LLM local: {e}"

# Extrai texto do PDF
def extrair_texto_pdf(caminho_pdf):
    texto = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                pagina = page.extract_text()
                if pagina:
                    texto += pagina + "\n"
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
    return texto

# Divide texto em blocos menores (para PDFs grandes)
def dividir_texto_em_blocos(texto, tamanho_maximo=3000):
    blocos = []
    while len(texto) > tamanho_maximo:
        corte = texto.rfind("\n", 0, tamanho_maximo)
        corte = corte if corte != -1 else tamanho_maximo
        blocos.append(texto[:corte])
        texto = texto[corte:]
    if texto.strip():
        blocos.append(texto)
    return blocos

# Processa todos os PDFs
def processar_projetos_com_llm():
    resultados = []

    for arquivo in os.listdir(PASTA_PDFS):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(PASTA_PDFS, arquivo)
            print(f"🧾 Processando: {arquivo}")
            texto = extrair_texto_pdf(caminho)

            if texto:
                blocos = dividir_texto_em_blocos(texto)
                respostas_blocos = []

                for i, bloco in enumerate(blocos):
                    print(f"🔹 Consultando bloco {i+1}/{len(blocos)}...")
                    resposta = consultar_llm(bloco)
                    respostas_blocos.append(resposta)

                resposta_final = "\n---\n".join(respostas_blocos)
                resultados.append(f"📄 {arquivo}\n{resposta_final}")
            else:
                resultados.append(f"📄 {arquivo}\nTexto não encontrado ou não extraído.")

    return resultados

# Salva em JSON
def salvar_resultados_em_json(resultados, caminho_arquivo="resultados_projeto_engenharia.json"):
    dados_para_salvar = []
    for resultado in resultados:
        dados = {
            "arquivo": resultado.split("\n")[0],
            "resposta": "\n".join(resultado.split("\n")[1:])
        }
        dados_para_salvar.append(dados)

    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)
        print(f"✅ Resultados salvos com sucesso em {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar os resultados em JSON: {e}")

# 🔁 FLUXO PRINCIPAL
if __name__ == "__main__":
    resultados = processar_projetos_com_llm()
    salvar_resultados_em_json(resultados)
