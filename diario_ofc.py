from imports import *
from celery_config import app
from openai import OpenAI

PASTA_PDFS = r"C:\\Users\\aesouza\\Desktop\\diario_ofc"


client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

def consultar_llm(prompt):
    try:
        resposta = client.chat.completions.create(
            model="llama3:8b",
            messages=[
                {"role": "system", "content": "Você é um especialista em analisar textos do Diário Oficial. Extraia pessoas nomeadas ou exoneradas com seus cargos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar LLM local: {e}"

def apagar_arquivos_pasta(PASTA_PDFS):
    if not os.path.exists(PASTA_PDFS):
        print(f"A pasta '{PASTA_PDFS}' não existe.")
        return
    for arquivo in os.listdir(PASTA_PDFS):
        caminho = os.path.join(PASTA_PDFS, arquivo)
        try:
            if os.path.isfile(caminho):
                os.remove(caminho)
            elif os.path.isdir(caminho):
                shutil.rmtree(caminho)
        except Exception as e:
            print(f"Erro ao apagar {caminho}: {e}")

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            pagina = page.extract_text()
            if pagina:
                texto += pagina + "\n"
    return texto

def processar_diarios_com_llm():
    resultados = []
    for arquivo in os.listdir(PASTA_PDFS):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(PASTA_PDFS, arquivo)
            print(f"🧾 Processando: {arquivo}")
            texto = extrair_texto_pdf(caminho)
            resposta = consultar_llm(f"Extraia as nomeações e exonerações deste conteúdo:\n\n{texto}")
            print(f"✅ Resultado:\n{resposta}")
            resultados.append(f"📄 {arquivo}\n{resposta}")
    return resultados

def download_pdf(edicoes):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": PASTA_PDFS,
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False
    })
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    data = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    if datetime.today().strftime("%A") == "Monday":
        data = (datetime.now() - timedelta(days=3)).strftime('%Y_%m_%d')

    try:
        for edicao in edicoes:
            url = f"https://diof.io.org.br/api/diario-oficial/download/{data}{edicao}004611.pdf"
            driver.get(url)
            time.sleep(5)
    finally:
        time.sleep(10)
        driver.quit()

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    url = "https://laurodefreitas.ba.gov.br/2022/"
    button_selector = 'body > header > div > div > div.header-top.black-bg.d-none.d-md-block > div > div > div > div.btn-group > a:nth-child(2) > button'
    table_selector = "#edicoesAnteriores > div.table-responsive > table > tbody"
    edition_column_selector = "#edicoesAnteriores > div.table-responsive > table > tbody > tr > td:nth-child(2)"
    edicoes = []
    page.on("popup", lambda popup: edicoes.extend(handle_popup(popup, table_selector, edition_column_selector)))
    page.goto(url)
    page.click(button_selector)
    page.wait_for_timeout(30000)
    browser.close()
    return edicoes

def handle_popup(popup, table_selector, edition_column_selector):
    data = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    if datetime.today().strftime("%A") == "Monday":
        data = (datetime.now() - timedelta(days=3)).strftime("%d/%m/%Y")

    edicoes = []
    try:
        popup.wait_for_selector(table_selector)
        for i in range(1, 10):
            data_linha = popup.query_selector_all(
                f"#edicoesAnteriores > div.table-responsive > table > tbody > tr:nth-child({i}) > td:nth-child(1)"
            )[0].text_content().strip()
            if data_linha == data:
                texto = popup.query_selector_all(
                    f"#edicoesAnteriores > div.table-responsive > table > tbody > tr:nth-child({i}) > td:nth-child(2)"
                )[0].text_content().strip()
                edicoes.append(texto)
    except Exception as e:
        print(f"Erro ao capturar edições: {e}")
    return edicoes

def enviar_email(conteudo):
    data = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    if datetime.today().strftime("%A") == "Monday":
        data = (datetime.now() - timedelta(days=3)).strftime("%d/%m/%Y")

    assunto = f"Nomeações e Exonerações - Diário Oficial {data}"
    msg = MIMEMultipart()
    msg["From"] = "bot.diario.lf@gmail.com"
    msg["To"] = "dtic-secad@laurodefreitas.ba.gov.br"
    msg["Subject"] = assunto

    corpo = "\n\n---\n\n".join(conteudo) if conteudo else "Nenhuma nomeação ou exoneração encontrada."
    msg.attach(MIMEText(corpo, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login("bot.diario.lf@gmail.com", os.getenv("EMAIL_SENHA"))
        servidor.sendmail(msg["From"], msg["To"], msg.as_string())
        servidor.quit()
        print("📧 E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

@app.task
def run_full_process():
    with sync_playwright() as playwright:
        edicoes = run(playwright)
        download_pdf(edicoes)
        resultados = processar_diarios_com_llm()
        enviar_email(resultados)
        apagar_arquivos_pasta(PASTA_PDFS)
