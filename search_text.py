from imports import *
from webdriver_setup import webdriver_setup


def acesso_pmlf(url, file_path):
    # Configurações do navegador
    options = Options()
    options.add_argument("--start-maximized") 
    options.add_experimental_option('prefs', {
        "download.default_directory": file_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Inicializar o navegador
    driver, wait = webdriver_setup()

    # Acessar a URL
    driver.get(url)

    # Acessar o link do PDF
    wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/header/div/div/div[1]/div/div/div/div[2]/a[2]/button'))).click()
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="navbarNav"]/ul/li[3]').click()
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="edicoesAnteriores"]/div[3]/table/tbody/tr[1]/td[4]/button[2]').click()
    time.sleep(5)
    download_element = driver.find_element(By.XPATH, '//*[@id="embed-diario"]')
    link_download = download_element.get_attribute('src')
    return link_download

def download_pdf(url, file_path):
    link_download = download_pdf(url, file_path)
    pdf = requests.get(link_download)
    return pdf


# Função para ler o PDF e separar o texto
def ler_pdf_e_processar(pdf_path):
    # Abrir o arquivo PDF
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        texto = ""
        
        # Extrair texto de cada página
        for page in reader.pages:
            texto += page.extract_text()
    
    # Normalizar o texto para maiúsculas e dividir com base na palavra "DECRETA"
    partes = re.split(r'\s*DECRETA\s*', texto.upper())
    
    # A primeira parte será a anterior ao primeiro "DECRETA"
    partes = [partes[1]] + partes[1:]  # Inclui o texto anterior ao primeiro "DECRETA"
    
    # Filtrando as partes que contêm as palavras "nomeia" ou "exonera"
    partes_filtradas = [parte for parte in partes if "NOMEIA" in parte or "EXONERA" in parte]
    
    return partes_filtradas

# Caminho do arquivo PDF
pdf_path = "teste.pdf"
url = "https://laurodefreitas.ba.gov.br/2022/"


acesso_pmlf(url, pdf_path)
download_pdf(url, pdf_path)
# Chama a função e imprime as partes filtradas
partes_filtradas = ler_pdf_e_processar(pdf_path)
for i, parte in enumerate(partes_filtradas):
    print(f"Parte {i+1}:")
    print(parte)
    print("\n---\n")
