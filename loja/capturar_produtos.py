from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains

def webdriver_setup():
    # Caminho para o ChromeDriver
    extension_path = r'c:\Users\aesouza\AppData\Local\Google\Chrome\User Data\Default\Extensions\dcngeagmmhegagicpcmpinaoklddcgon\2.17.0_0'
    # extension_path = r'c:\Users\Albano Souza\AppData\Local\Google\Chrome\User Data\Default\Extensions\dcngeagmmhegagicpcmpinaoklddcgon\2.17.0_0'
    chrome_options = Options()
    chrome_options.add_argument(f'--load-extension={extension_path}')


    #INICIALIZA DRIVER
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10, poll_frequency=2)  # Aguarda até 10 segundos
    return driver, wait

driver, wait = webdriver_setup()
url = "https://www.racymodas.com.br/moda-fitness?pagina=1"
driver.get(url)
time.sleep(5)

elements = driver.find_elements(By.CLASS_NAME, "fbits-item-lista-spot ")
for element in elements:

    # Rolando até o elemento com JavaScript
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(1)  # Pausa para garantir que a rolagem seja concluída
    # Clicando no elemento com ActionChains para evitar interceptação
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

    time.sleep(2)
    nome = driver.find_element(By.CLASS_NAME, "fbits-produto-nome").text
    sku = driver.find_element(By.CLASS_NAME, "fbits-sku").text
    precos = driver.find_elements(By.XPATH, "//*[@id='imagem-pagina-produto']/div[1]/div")
    if len(precos) > 1:
        preco_normal = precos[0].text
        preco_desconto = precos[1].text
    else:
        preco_normal = precos[0].text
        preco_desconto = "Sem desconto"
    driver.back()

    print(f" Nome: {nome}, SKU: {sku}, Preco Normal: {preco_normal}, Preco Final: {preco_desconto}")