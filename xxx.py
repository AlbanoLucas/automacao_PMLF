from imports import *


# Diretório onde os arquivos serão baixados
download_directory = r'c:\Users\Albano Souza\Downloads'

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': download_directory,
    'plugins.always_open_pdf_externally': True,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True
})

# Inicializa o navegador com as opções configuradas
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
data = datetime.now().strftime('%Y_%m_%d')
doc = '3144'
try:
    # URL do PDF que deseja baixar
    pdf_url = f'https://diof.io.org.br/api/diario-oficial/download/{data}{doc}004611.pdf'

    # Acessa a URL do PDF
    driver.get(pdf_url)

    # Aguarda o download ser concluído
    time.sleep(5)  # Ajuste o tempo conforme necessário

finally:
    # Fecha o navegador
    driver.quit()
