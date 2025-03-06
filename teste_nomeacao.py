import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    """Extrai o texto do PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        texto = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return texto

def extract_appointments(text):
    """Extrai nomeações de pessoas e seus cargos do texto."""
    nomeacoes = []
    
    # Expressão regular para capturar nomeações
    padrao = re.compile(r"(?P<cargo>.*?)\s*(Titular|Suplente):\s*(?P<nome>[A-Z][a-zA-Z\s]+)")
    
    for match in padrao.finditer(text):
        cargo = match.group("cargo").strip()
        nome = match.group("nome").strip()
        nomeacoes.append((nome, cargo))
    
    return nomeacoes

def print_appointments(appointments):
    """Imprime as nomeações formatadas."""
    if appointments:
        print("\nNomeações encontradas:")
        for nome, cargo in appointments:
            print(f"- {nome} – {cargo}")
    else:
        print("Nenhuma nomeação encontrada.")

if __name__ == "__main__":
    pdf_path = "teste.pdf"  # Substitua pelo caminho correto do PDF
    texto_extraido = extract_text_from_pdf(pdf_path)
    nomeacoes = extract_appointments(texto_extraido)
    print_appointments(nomeacoes)
