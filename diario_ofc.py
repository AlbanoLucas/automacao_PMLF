from imports import *
logging.getLogger("pdfminer").setLevel(logging.ERROR)

PASTA_PDFS = r"C:\\Users\\aesouza\\Desktop\\diario_ofc"
PASTA_DESTINO = r"C:\\Users\\aesouza\\Desktop\\diario_mes"

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

def consultar_llm(prompt):
    try:
        resposta = client.chat.completions.create(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content":
                    "Você é um especialista em atos administrativos do Diário Oficial.\n"
                    "Sua tarefa é identificar exclusivamente:\n"
                    "- Nomeações (ex: nomeado, nomeada, designado, admitido)\n"
                    "- Exonerações (ex: exonerado, exonerada, dispensado, desligado)\n"
                    "- Retificações (ex: corrigido, alterado, ajustado)\n\n"
                    "Ignore qualquer conteúdo que não esteja claramente relacionado a esses atos.\n"
                    "Para cada ocorrência encontrada, retorne no formato:\n"
                    "Nome: [NOME COMPLETO] - Secretaria: [SECRETARIA] - Ato: [NOMEAÇÃO | EXONERAÇÃO | RETIFICAÇÃO]\n"
                },
                {"role": "user", "content": f"Texto para análise:\n{prompt}"}
            ],
            temperature=0.0,
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar LLM local: {e}"

def mover_arquivos_pasta(pasta_origem, pasta_destino):
    if not os.path.exists(pasta_origem):
        print(f"A pasta '{pasta_origem}' não existe.")
        return

    # Cria a pasta de destino, se não existir
    os.makedirs(pasta_destino, exist_ok=True)

    for arquivo in os.listdir(pasta_origem):
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        try:
            if os.path.isfile(caminho_origem) or os.path.isdir(caminho_origem):
                shutil.move(caminho_origem, caminho_destino)
                print(f"Movido: {arquivo}")
        except Exception as e:
            print(f"Erro ao mover {caminho_origem}: {e}")

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
            texto += "\n"
    return texto

def dividir_por_artigos_relevantes(texto):
    artigos = re.split(r"\n?Art\.\s*\d+[\u00bao]?[.\s]", texto)
    artigos_filtrados = []
    for artigo in artigos:
        trecho = artigo.strip()
        if any(palavra in trecho.lower() for palavra in ["exoner", "nomea", "retific", "designad"]):
            artigos_filtrados.append("Art. " + trecho)
    return artigos_filtrados

def processar_diarios_com_llm():
    resultados = []
    for arquivo in os.listdir(PASTA_PDFS):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(PASTA_PDFS, arquivo)
            print(f"Processando: {arquivo}")
            texto = extrair_texto_pdf(caminho)
            artigos_relevantes = dividir_por_artigos_relevantes(texto)
            respostas_arquivo = []
            for i, artigo in enumerate(artigos_relevantes):
                resposta = consultar_llm(artigo)
                respostas_arquivo.append(f"Trecho {i+1}:\n{resposta}")
            resposta_final = "\n".join(respostas_arquivo) if respostas_arquivo else "Nenhum ato relevante encontrado."
            print(f"Resultado: {resposta_final}")
            resultados.append(f"{arquivo}\n{resposta_final}")
    return resultados

def download_pdf_requests(edicoes, pasta_destino, max_tentativas=3, intervalo=5):
    data = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    if datetime.today().strftime("%A") == "Monday":
        data = (datetime.now() - timedelta(days=3)).strftime('%Y_%m_%d')
    # data = '2025_05_06'

    for edicao in edicoes:
        url = f"https://diof.io.org.br/api/diario-oficial/download/{data}{edicao}004611.pdf"
        destino = os.path.join(pasta_destino, f"{data}{edicao}004611.pdf")
        
        tentativas = 0
        sucesso = False

        while tentativas < max_tentativas and not sucesso:
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()

                with open(destino, "wb") as f:
                    f.write(response.content)
                print(f"PDF baixado: {destino}")
                sucesso = True

            except requests.exceptions.Timeout:
                print(f"Timeout ao tentar baixar: {url}")
            except requests.exceptions.ConnectionError:
                print(f"Erro de conexão ao acessar: {url}")
            except requests.exceptions.HTTPError as e:
                print(f"Erro HTTP ({e.response.status_code}) ao baixar: {url}")
                break  
            except requests.exceptions.RequestException as e:
                print(f"Erro inesperado ao baixar {url}: {e}")
            
            tentativas += 1
            if not sucesso and tentativas < max_tentativas:
                print(f"🔁 Tentando novamente em {intervalo} segundos... ({tentativas}/{max_tentativas})")
                time.sleep(intervalo)

        if not sucesso:
            print(f"Falha ao baixar após {max_tentativas} tentativas: {url}")

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
    # data = '06/05/2025'

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
    # data = '06/05/2025'

    assunto = f"Nomeações e Exonerações - Diário Oficial {data}"
    msg = MIMEMultipart()
    msg["From"] = "bot.diario.lf@gmail.com"
    msg["To"] = "dtic-secad@laurodefreitas.ba.gov.br"
    # msg["To"] = "albanolucas23@gmail.com"
    msg["Subject"] = assunto

    corpo = "\n\n---\n\n".join(conteudo) if conteudo else "Nenhuma nomeação ou exoneração encontrada."
    msg.attach(MIMEText(corpo, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login("bot.diario.lf@gmail.com", os.getenv("EMAIL_SENHA"))
        servidor.sendmail(msg["From"], msg["To"], msg.as_string())
        servidor.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# @app.task
# def run_full_process():
with sync_playwright() as playwright:
    edicoes = run(playwright)
    print(f"Edições encontradas: {edicoes}")
    download_pdf_requests(edicoes, PASTA_PDFS)
    resultados = processar_diarios_com_llm()
    enviar_email(resultados)
    mover_arquivos_pasta(PASTA_PDFS, PASTA_DESTINO)
