import PyPDF2
import spacy

# Carregar o modelo de linguagem para o português
nlp = spacy.load("pt_core_news_sm")

def extract_names_and_positions(pdf_file):
    # Abrir o arquivo PDF
    with open(pdf_file, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        
        # Extrair o texto do PDF
        text = ''
        for page in pdf.pages:
            text += page.extract_text()

    # Análise de texto com spaCy
    doc = nlp(text)

    # Encontrar entidades nomeadas (nomes de pessoas)
    entities = [(entity.text, entity.label_) for entity in doc.ents if entity.label_ == "PERSON"]

    # Encontrar frases que contenham informações de cargo
    positions = []
    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "NOUN" and token.lemma_ in ["cargo", "função", "posição", "papel"]:
                positions.append((sent.text, token.lemma_))

    # Combina entidades nomeadas com informações de cargo
    appointments = []
    for entity, _ in entities:
        for sent, _ in positions:
            if entity in sent:
                appointments.append((entity, sent))

    return appointments

# Exemplo de uso
pdf_file = 'teste.pdf'
appointments = extract_names_and_positions(pdf_file)
for name, position in appointments:
    print(f'{name} - {position}')