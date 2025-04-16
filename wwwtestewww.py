import os
import pdfplumber
from openai import OpenAI
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

PASTA_PDFS = r"C:\\Users\\Albano\\Desktop\\projetos_engenharia_ambiental"
PASTA_SAIDA = "resumos_txt"
os.makedirs(PASTA_SAIDA, exist_ok=True)

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

PROMPT_SISTEMA = (
    """Você é um especialista em engenharia ambiental renomado. Sua tarefa é analisar artigos e gerar um resumo técnico completo,
    mantendo todos os dados relevantes do projeto.
    O resumo deve incluir: objetivos, metodologia, resultados e conclusões e informações abordando o que foi apresentado na revisão bibliográfica.
    Use linguagem técnica e precisa, evitando jargões desnecessários.
    O resumo deve ser claro e conciso, com foco em informações essenciais, sem repetições."""
)

def consultar_llm(texto_completo):
    try:
        resposta = client.chat.completions.create(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": texto_completo}
            ],
            temperature=0.2
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar LLM local: {e}"

def extrair_texto_simples(caminho_pdf):
    texto = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                pagina = page.extract_text()
                if pagina:
                    texto += pagina + "\n"
    except Exception as e:
        print(f"Erro ao extrair texto do PDF '{caminho_pdf}': {e}")
    return texto

def processar_pdf(caminho_pdf, nome_arquivo):
    print(f"🧾 Processando: {nome_arquivo}")
    texto_completo = extrair_texto_simples(caminho_pdf)

    if not texto_completo.strip():
        print("⚠️ PDF sem texto extraído.")
        return

    print("🔍 Enviando texto completo para LLM...")
    resumo = consultar_llm(texto_completo)
    salvar_em_txt(nome_arquivo, resumo)

def salvar_em_txt(nome_arquivo, resumo):
    nome_base = os.path.splitext(nome_arquivo)[0]
    caminho_saida = os.path.join(PASTA_SAIDA, f"{nome_base}_resumo.txt")
    try:
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(resumo)
        print(f"✅ Resumo salvo em: {caminho_saida}")
    except Exception as e:
        print(f"Erro ao salvar resumo: {e}")

# 🚀 FLUXO PRINCIPAL
if __name__ == "__main__":
    for arquivo in os.listdir(PASTA_PDFS):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(PASTA_PDFS, arquivo)
            processar_pdf(caminho, arquivo)
