from imports import *

# Caminho da pasta com os PDFs
PASTA_PDFS = r"C:\Users\Albano Souza\Desktop\diario_ofc"

def ler_pdf_e_processar(pdf_path):
    """Lê um PDF e filtra partes que contenham 'NOMEIA' ou 'EXONERA'."""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
    partes = re.split(r'\s*DECRETA\s*', texto.upper())
    partes_filtradas = [parte for parte in partes if "NOMEIA" in parte or "EXONERA" in parte or "NOMEADO" in parte]
    return partes_filtradas

def nomeacoes_exoneracoes():
    if os.path.exists(PASTA_PDFS):
        for arquivo in os.listdir(PASTA_PDFS):
            if arquivo.lower().endswith('.pdf'):
                caminho_pdf = os.path.join(PASTA_PDFS, arquivo)
                print(f"\n🔍 Processando: {arquivo}")
                partes_filtradas = ler_pdf_e_processar(caminho_pdf)
                if partes_filtradas:
                    for i, parte in enumerate(partes_filtradas):
                        print(f"\n📜 Parte {i+1}:\n{parte}\n---")
                else:
                    print("⚠️ Nenhuma nomeação ou exoneração encontrada.\n")
    else:
        print(f"⚠️ A pasta {PASTA_PDFS} não existe.")

