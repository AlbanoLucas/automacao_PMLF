from imports import *
import camelot

# Caminho da pasta com os PDFs
PASTA_PDFS = r"C:\Users\aesouza\Desktop\diario_ofc"

def ler_pdf_e_processar(pdf_path):
    """Lê um PDF, extrai texto e tabelas, e filtra partes que contenham 'NOMEIA' ou 'EXONERA'."""
    resultados = []

    # Extração de texto
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
    partes = re.split(r'\s*DECRETA\s*', texto.upper())
    partes_filtradas = [parte for parte in partes if "NOMEIA" in parte or "EXONERA" in parte or "NOMEADO" in parte]

    for parte in partes_filtradas:
        resultados.append({"tipo": "texto", "conteudo": parte})

    # Extração de tabelas
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
        for table in tables:
            resultados.append({"tipo": "tabela", "conteudo": table.df})
    except Exception as e:
        print(f"Erro ao extrair tabelas de {pdf_path}: {e}")

    return resultados

def nomeacoes_exoneracoes():
    arquivo_csv = "resultados.csv"
    
    if os.path.exists(PASTA_PDFS):
        dados = []
        
        for arquivo in os.listdir(PASTA_PDFS):
            if arquivo.lower().endswith('.pdf'):
                caminho_pdf = os.path.join(PASTA_PDFS, arquivo)
                print(f"\n🔍 Processando: {arquivo}")
                partes_filtradas = ler_pdf_e_processar(caminho_pdf)
                
                if partes_filtradas:
                    for i, parte in enumerate(partes_filtradas):
                        if parte["tipo"] == "tabela":
                            conteudo = parte["conteudo"].to_csv(index=False)
                        else:
                            conteudo = parte["conteudo"]
                        dados.append([arquivo, i + 1, parte["tipo"], conteudo])
                else:
                    dados.append([arquivo, "N/A", "N/A", "Nenhuma nomeação ou exoneração encontrada."])
        
        df = pd.DataFrame(dados, columns=["Arquivo", "Parte", "Tipo", "Conteudo"])
        df.to_csv(arquivo_csv, index=False, encoding="utf-8")
        
        print(f"✅ Resultados salvos em {arquivo_csv}")
    else:
        print(f"⚠️ A pasta {PASTA_PDFS} não existe.")

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
    data = datetime.now().strftime('%Y_%m_%d')
    try:
        for edicao in edicoes: 
            pdf_url = f'https://diof.io.org.br/api/diario-oficial/download/{data}{edicao}004611.pdf'
            driver.get(pdf_url)
            time.sleep(5) 
    finally:
        time.sleep(20)
        driver.quit()

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    url = 'https://laurodefreitas.ba.gov.br/2022/'
    page.goto(url)
    button_selector = 'body > header > div > div > div.header-top.black-bg.d-none.d-md-block > div > div > div > div.btn-group > a:nth-child(2) > button'
    table_selector = '#edicoesAnteriores > div.table-responsive > table > tbody'
    edition_column_selector = '#edicoesAnteriores > div.table-responsive > table > tbody > tr > td:nth-child(2)'
    edicoes = []
    page.on('popup', lambda popup: edicoes.extend(handle_popup(popup, table_selector, edition_column_selector)))
    page.click(button_selector)
    page.wait_for_timeout(5000) 
    page.wait_for_load_state('domcontentloaded')
    browser.close()
    return edicoes

def handle_popup(popup, table_selector, edition_column_selector):
    data = datetime.now().strftime('%d/%m/%Y')
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

with sync_playwright() as playwright:
    edicoes = run(playwright)
    download_pdf(edicoes) 
    nomeacoes_exoneracoes()