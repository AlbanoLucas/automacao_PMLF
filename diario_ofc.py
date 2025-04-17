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
            model="llama3.1:8b",
            messages=[ 
                {"role": "system", "content": 
                    "Você é um especialista em analisar textos do Diário Oficial. Sua tarefa é extrair os nomes das pessoas, seus cargos e se elas foram nomeadas, exoneradas ou teve retificação em seus cargos ou nomes, caso haja retificação não identificar como nomeação ou exoneração e sim como retificação. /n"
                    "Os atos administrativos, como 'nomeação', 'exoneração' ou 'retificação', podem estar representados através de sinonimos. /n"
                    "Você deve ignorar qualquer outro conteúdo que não se refira diretamente a esses atos administrativos. "                    
                },
                {"role": "user", "content": 
                    "Texto para análise:\n"
                    f"{prompt}"} 
            ],
            temperature=0.0,
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

    def reconstruir_tabela_por_layout(words, tolerancia_coluna=10):
        if not words:
            return ""

        # Agrupa palavras por linha (posição y)
        linhas_dict = {}
        for word in words:
            y = round(word['top'], 1)
            if y not in linhas_dict:
                linhas_dict[y] = []
            linhas_dict[y].append(word)

        texto_linhas = []
        for y in sorted(linhas_dict.keys()):
            linha = linhas_dict[y]
            linha_ordenada = sorted(linha, key=lambda w: w["x0"])
            
            # Agrupa por colunas aproximadas (com base em distância entre palavras)
            colunas = []
            coluna_atual = [linha_ordenada[0]['text']]
            for i in range(1, len(linha_ordenada)):
                dist = linha_ordenada[i]['x0'] - linha_ordenada[i-1]['x1']
                if dist > tolerancia_coluna:
                    colunas.append(" ".join(coluna_atual))
                    coluna_atual = [linha_ordenada[i]['text']]
                else:
                    coluna_atual.append(linha_ordenada[i]['text'])
            colunas.append(" ".join(coluna_atual))

            texto_linhas.append("\t".join(colunas))
        
        return "\n".join(texto_linhas)

    with pdfplumber.open(caminho_pdf) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                tabelas = page.extract_tables()
                if tabelas:
                    for tabela in tabelas:
                        for linha in tabela:
                            if linha:
                                texto += "\t".join(col.strip() if col else "" for col in linha) + "\n"
                else:
                    words = page.extract_words()
                    if words:
                        texto += reconstruir_tabela_por_layout(words) + "\n"
                    else:
                        pagina = page.extract_text()
                        if pagina:
                            texto += pagina + "\n"
            except Exception as e:
                print(f"⚠️ Erro na página {page_num} do PDF '{caminho_pdf}': {e}")
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

def download_pdf_requests(edicoes, pasta_destino, max_tentativas=3, intervalo=5):
    data = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    if datetime.today().strftime("%A") == "Monday":
        data = (datetime.now() - timedelta(days=3)).strftime('%Y_%m_%d')

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
                print(f"✅ PDF baixado: {destino}")
                sucesso = True

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout ao tentar baixar: {url}")
            except requests.exceptions.ConnectionError:
                print(f"❌ Erro de conexão ao acessar: {url}")
            except requests.exceptions.HTTPError as e:
                print(f"⚠️ Erro HTTP ({e.response.status_code}) ao baixar: {url}")
                break  # se for 404 ou 500, não adianta tentar de novo
            except requests.exceptions.RequestException as e:
                print(f"🚫 Erro inesperado ao baixar {url}: {e}")
            
            tentativas += 1
            if not sucesso and tentativas < max_tentativas:
                print(f"🔁 Tentando novamente em {intervalo} segundos... ({tentativas}/{max_tentativas})")
                time.sleep(intervalo)

        if not sucesso:
            print(f"❌ Falha ao baixar após {max_tentativas} tentativas: {url}")

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
    # msg["To"] = "dtic-secad@laurodefreitas.ba.gov.br"
    msg["To"] = "albanolucas23@gmail.com"
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

# @app.task
# def run_full_process():
with sync_playwright() as playwright:
    # edicoes = run(playwright)
    # print(f"🗂️ Edições encontradas: {edicoes}")
    # download_pdf_requests(edicoes)
    resultados = processar_diarios_com_llm()
    enviar_email(resultados)
    # apagar_arquivos_pasta(PASTA_PDFS)
