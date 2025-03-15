from playwright.sync_api import sync_playwright
from datetime import datetime
from xxx import *
from search_text import *

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Defina a URL alvo
    url = 'https://laurodefreitas.ba.gov.br/2022/'

    # Navegue até a página
    page.goto(url)

    # Defina o seletor do botão que abre a nova aba
    button_selector = 'body > header > div > div > div.header-top.black-bg.d-none.d-md-block > div > div > div > div.btn-group > a:nth-child(2) > button'

    # Defina o seletor da tabela na nova aba
    table_selector = '#edicoesAnteriores > div.table-responsive > table > tbody'

    # Defina o seletor das células da coluna "Edição"
    edition_column_selector = '#edicoesAnteriores > div.table-responsive > table > tbody > tr > td:nth-child(2)'

    # Lista para armazenar as edições
    edicoes = []

    # Adicione um ouvinte para o evento 'popup' para capturar a nova aba
    page.on('popup', lambda popup: edicoes.extend(handle_popup(popup, table_selector, edition_column_selector)))

    # Clique no botão que abre a nova aba
    page.click(button_selector)

    # Aguarde que a nova aba seja completamente carregada
    page.wait_for_timeout(5000)  # Aguarda mais tempo para garantir que o conteúdo foi carregado.

    # Aguarde até que o DOM seja carregado e visível
    page.wait_for_load_state('domcontentloaded')

    # Feche o navegador após a interação
    browser.close()

    # Retorne a lista de edições extraídas
    return edicoes

def handle_popup(popup, table_selector, edition_column_selector):
    data = datetime.now().strftime('%d/%m/%Y')
    # data = '14/03/2025'
    editions = []
    try:
        # Aguarde a tabela carregar na nova aba
        popup.wait_for_selector(table_selector)
        
        # Extraia os textos da coluna "Edição"
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

    # Retorna a lista de edições extraídas
    return editions

# Execução do código
with sync_playwright() as playwright:
    edicoes = run(playwright)
    download_pdf(edicoes)  # Adapte conforme a necessidade de baixar o PDF
    nomeacoes_exoneracoes()  # Processamento das nomeações