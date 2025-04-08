from imports import *
from celery_config import app

# Caminho da pasta com os PDFs
# PASTA_PDFS = r"/home/albano/Documentos/diario_ofc"
PASTA_PDFS = r"C:\Users\aesouza\Desktop\diario_ofc"

def apagar_arquivos_pasta(PASTA_PDFS):
    #Apaga todos os arquivos de uma pasta especificada.
    if not os.path.exists(PASTA_PDFS):
        print(f"A pasta '{PASTA_PDFS}' não existe.")
        return
    
    for arquivo in os.listdir(PASTA_PDFS):
        caminho_arquivo = os.path.join(PASTA_PDFS, arquivo)
        try:
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
            elif os.path.isdir(caminho_arquivo):
                shutil.rmtree(caminho_arquivo)  # Remove pastas e seus conteúdos
            print(f"Removido: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao remover {caminho_arquivo}: {e}")

def extrair_nomeacoes_exoneracoes():
    """Extrai partes de PDFs """
    todas_partes_filtradas = []

    if not os.path.exists(PASTA_PDFS):
        print(f"⚠️ A pasta {PASTA_PDFS} não existe.")
        return todas_partes_filtradas

    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.lower().endswith('.pdf'):
            continue

        caminho_pdf = os.path.join(PASTA_PDFS, arquivo)
        print(f"\n🔍 Processando: {arquivo}")

        texto = ""

        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n"

        texto_upper = texto.upper()
        partes = re.split(r'\s*ART.\s*', texto_upper)

        # Extrai trecho entre "ANEXO ÚNICO" e "RETIFICAÇÃO", sem incluir "RETIFICAÇÃO"
        trecho_anexo_unico = ""
        match_anexo = re.search(r"(ANEXO ÚNICO – DECRETO.*?)(?=RETIFICAÇÃO)", texto_upper, flags=re.DOTALL)
        if match_anexo:
            trecho_anexo_unico = match_anexo.group(1).strip()

        for parte in partes:
            if any(kw in parte for kw in ["NOMEIA", "NOMEAÇÃO", "EXONERA", "NOMEADO", "NOMEADA", "EXONERADO", "EXONERADA"]):
                if any(skip_kw in parte for skip_kw in ["REGULARIZAR SITUAÇÃO DE ACÚMULO DE CARGO", "RETIFICA"]):
                    continue

                todas_partes_filtradas.append(parte)
                print(f"\n📜 Parte {len(todas_partes_filtradas)}:\n{parte}\n---")

                if "ANEXO ÚNICO" in parte and trecho_anexo_unico:
                    todas_partes_filtradas.append(trecho_anexo_unico)
                    print(f"\n📎 Anexo Único Adicionado:\n{trecho_anexo_unico}\n---")

        if not todas_partes_filtradas:
            print("⚠️ Nenhuma nomeação ou exoneração encontrada.\n")
        
    return todas_partes_filtradas
        
def download_pdf(edicoes):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': PASTA_PDFS,
        'plugins.always_open_pdf_externally': True,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True
    })
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    data = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    dia = datetime.today().strftime("%A")
    if dia == 'Monday':
        data = (datetime.now() - timedelta(days=3)).strftime('%Y_%m_%d')
    # data = '2025_04_08'
    
    try:
        for edicao in edicoes:  
            pdf_url = f'https://diof.io.org.br/api/diario-oficial/download/{data}{edicao}004611.pdf'
            driver.get(pdf_url)
            time.sleep(5)  

    finally:
        time.sleep(20)
        driver.quit()

def run(playwright):
    """Tratando app angular"""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    url = 'https://laurodefreitas.ba.gov.br/2022/'
    page.goto(url)
    #seletor do botão que abre diario
    button_selector = 'body > header > div > div > div.header-top.black-bg.d-none.d-md-block > div > div > div > div.btn-group > a:nth-child(2) > button'
    #seletor da tabela no diario
    table_selector = '#edicoesAnteriores > div.table-responsive > table > tbody'
    #seletor das células da coluna "Edição"
    edition_column_selector = '#edicoesAnteriores > div.table-responsive > table > tbody > tr > td:nth-child(2)'
    edicoes = []
    page.on('popup', lambda popup: edicoes.extend(handle_popup(popup, table_selector, edition_column_selector)))
    page.click(button_selector)
    page.wait_for_timeout(50000)  
    page.wait_for_load_state('domcontentloaded')
    browser.close()
    return edicoes

def handle_popup(popup, table_selector, edition_column_selector):
    """Tratando poup-up app angular"""
    data = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    dia = datetime.today().strftime("%A")
    if dia == 'Monday':
        data = (datetime.now() - timedelta(days=3)).strftime('%d/%m/%Y')
    # data = '08/04/2025'
 
    editions = []
    try:
        popup.wait_for_selector(table_selector)
        for i in range(1, 10):
            data_linha = popup.query_selector_all(f'#edicoesAnteriores > div.table-responsive > table > tbody > tr:nth-child({i}) > td:nth-child(1)')[0].text_content()
            data_linha = data_linha.strip()
            if data_linha in data:
                rows = popup.query_selector_all(f'#edicoesAnteriores > div.table-responsive > table > tbody > tr:nth-child({i}) > td:nth-child(2)')
                if rows:
                    text_edition = rows[0].text_content().strip()
                    editions.append(text_edition)
    except Exception as e:
        print(f"Erro ao extrair dados da pop-up: {e}")
    return editions

def enviar_email(texto):
    data = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    dia = datetime.today().strftime("%A")
    if dia == 'Monday':
        data = (datetime.now() - timedelta(days=3)).strftime('%d/%m/%Y')
    # data = '08/04/2025'

    # Configurações do e-mail
    # destinatario = "albanosouza0@gmail.com"
    destinatario = "dtic-secad@laurodefreitas.ba.gov.br"
    assunto = f"Resumo Diário Oficial {data}"
    smtp_servidor = "smtp.gmail.com"  # Altere conforme necessário
    smtp_porta = 587
    email_remetente = "bot.diario.lf@gmail.com"  # Substitua pelo seu e-mail
    senha = os.getenv("EMAIL_SENHA")

    # Criando a mensagem
    msg = MIMEMultipart()
    msg["From"] = email_remetente
    msg["To"] = destinatario
    msg["Subject"] = assunto
    
    if texto is None:
        msg.attach(MIMEText("Nenhuma nomeação ou exoneração encontrado.", "plain"))
    else:
        msg.attach(MIMEText("\n\n---\n\n".join(texto), "plain"))

    try:
        # Conectar ao servidor SMTP e enviar o e-mail
        servidor = smtplib.SMTP(smtp_servidor, smtp_porta)
        servidor.starttls()
        servidor.login(email_remetente, senha)
        servidor.sendmail(email_remetente, destinatario, msg.as_string())
        servidor.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# @app.task
# def run_full_process():
with sync_playwright() as playwright:
    edicoes = run(playwright)
    download_pdf(edicoes)  
    texto = extrair_nomeacoes_exoneracoes()  
    enviar_email(texto)
    apagar_arquivos_pasta(PASTA_PDFS)
        
