import os
import pdfplumber
from openai import OpenAI
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

PASTA_PDFS = r"C:\\Users\\aesouza\\Desktop\\projetos_engenharia_ambiental"
PASTA_SAIDA = "resumos_txt"
os.makedirs(PASTA_SAIDA, exist_ok=True)

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

PROMPT_SISTEMA = (
    """Você é um especialista multidisciplinar com profundo conhecimento em engenharia ambiental, direito ambiental e análises técnicas de projetos. Seu objetivo é analisar documentos técnicos extraídos de PDFs e gerar um **resumo técnico claro, objetivo e completo**, escrito em **português do Brasil**.

    Leia atentamente o conteúdo enviado e extraia as informações mais relevantes. Quando aplicável, identifique e destaque os seguintes tópicos:

    - Objetivos do projeto
    - Metodologia empregada
    - Resultados encontrados
    - Conclusões e recomendações
    - Informações da revisão bibliográfica (caso existam)
    - Aspectos jurídicos e legais envolvidos (caso haja)
    - Detalhes técnicos e estruturais importantes (caso presentes)

    Adapte os tópicos à natureza do conteúdo. O resumo deve ser técnico, sem floreios, direto ao ponto e com precisão terminológica. Use linguagem profissional, mantendo o foco nas informações úteis para análises e decisões técnicas.

    **Por favor, sempre responda em português**."""
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

def segmentar_por_subtitulos(caminho_pdf):
    blocos = []
    bloco_atual = ""
    fonte_maior = 0

    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                words = page.extract_words(extra_attrs=["size"])
                for word in words:
                    size = word['size']
                    text = word['text']
                    if size > fonte_maior:
                        fonte_maior = size

                for word in words:
                    size = word['size']
                    text = word['text']
                    if size >= fonte_maior:
                        if bloco_atual.strip():
                            blocos.append(bloco_atual.strip())
                        bloco_atual = text + " "
                    else:
                        bloco_atual += text + " "

        if bloco_atual.strip():
            blocos.append(bloco_atual.strip())

    except Exception as e:
        print(f"Erro ao segmentar PDF '{caminho_pdf}': {e}")

    return blocos

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

if __name__ == "__main__":
    for arquivo in os.listdir(PASTA_PDFS):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(PASTA_PDFS, arquivo)
            processar_pdf(caminho, arquivo)
