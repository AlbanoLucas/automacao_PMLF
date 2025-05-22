import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json

def webdriver_setup():
    extension_path = r'c:\Users\Albano\AppData\Local\Google\Chrome\User Data\Default\Extensions\dcngeagmmhegagicpcmpinaoklddcgon\2.17.0_0'
    chrome_options = Options()
    chrome_options.add_argument(f'--load-extension={extension_path}')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10, poll_frequency=2)
    return driver, wait

def sanitize_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def download_image(url, save_path):
    try:
        if os.path.exists(save_path):
            print(f"Imagem já existe: {save_path}")
            return
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Imagem salva em: {save_path}")
    except requests.RequestException as e:
        print(f"Erro ao baixar a imagem ({url}): {e}")

def create_product_folder(nome):
    # Caminho raiz da pasta loja
    root_path = os.path.join(os.getcwd(), 'loja')
    os.makedirs(root_path, exist_ok=True)
    
    # Criar subpasta com o nome do produto
    folder_name = sanitize_folder_name(nome)
    product_path = os.path.join(root_path, folder_name)
    if not os.path.exists(product_path):
        os.makedirs(product_path)
        print(f"Pasta criada: {product_path}")
    return product_path

def save_product_info(folder_name, nome, sku, preco_normal, preco_desconto):
    file_path = os.path.join(folder_name, "info.json")  # Agora salva como .json
    nome = nome.split()
    nome_formatado = ' '.join(nome[:-2])
    data = {
        'nome': nome_formatado,
        'sku': sku,
        'preco_normal': preco_normal,
        'preco_desconto': preco_desconto
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Informações salvas em: {file_path}")
    except Exception as e:
        print(f"Erro ao salvar informações do produto ({nome}): {e}")

driver, wait = webdriver_setup()
url = "https://www.racymodas.com.br/moda-fitness?pagina=1"
driver.get(url)
time.sleep(5)

elements = driver.find_elements(By.CLASS_NAME, "fbits-item-lista-spot")
for element in elements:
    try:
        wait.until(EC.visibility_of(element))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        time.sleep(1)

        nome = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "fbits-produto-nome"))).text 
        sku = driver.find_element(By.CLASS_NAME, "fbits-sku").text
        precos = driver.find_elements(By.XPATH, "//*[@id='imagem-pagina-produto']/div[1]/div")
        
        if len(precos) > 1:
            preco_normal = precos[0].text
            preco_desconto = precos[1].text
        else:
            preco_normal = precos[0].text
            preco_desconto = "Sem desconto"

        # Criar pasta do produto dentro da pasta loja
        product_folder = create_product_folder(nome)

        # Salvando as informações do produto na mesma pasta das imagens
        save_product_info(product_folder, nome, sku, preco_normal, preco_desconto)

        # Baixando as imagens, exceto a última
        imagens_lista = driver.find_elements(By.CLASS_NAME, "fbits-produto-imagensMinicarrossel-item")
        for i, imagem in enumerate(imagens_lista[:-1], start=1):
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", imagem)
            imagem_url = imagem.find_element(By.TAG_NAME, "img").get_attribute("src")
            save_path = os.path.join(product_folder, f"imagem_{i}.jpg")
            download_image(imagem_url, save_path)

        driver.back()
        print(f"Produto: {nome} | SKU: {sku} | Preço Normal: {preco_normal} | Preço Desconto: {preco_desconto}")
    except Exception as e:
        print(f"Erro ao processar o produto '{nome}': {e}")
