import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import win32gui
import pyperclip


def copiar_para_area_transferencia(texto):
    try:
        pyperclip.copy(texto)
        print("Texto copiado para a área de transferência com sucesso!")
    except Exception as e:
        print(f"Erro ao copiar para a área de transferência: {e}")

def webdriver_setup():
    extension_path = r'c:\Users\Albano\AppData\Local\Google\Chrome\User Data\Default\Extensions\dcngeagmmhegagicpcmpinaoklddcgon\2.17.0_0'
    chrome_options = Options()
    chrome_options.add_argument(f'--load-extension={extension_path}')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10, poll_frequency=2)
    return driver, wait

def upload_imagens(nome_produto):
    try:
        # Caminho da pasta de imagens
        diretorio_imagens = r'C:\Users\Albano\Documents\GitHub\automacao_PMLF\loja'
        
        # Procurar uma pasta que comece com o nome do produto
        pasta_produto = None
        for pasta in os.listdir(diretorio_imagens):
            if pasta.lower().startswith(nome_produto.lower()):
                pasta_produto = os.path.join(diretorio_imagens, pasta)
                break

        # Garantir que encontrou a pasta
        if not pasta_produto or not os.path.isdir(pasta_produto):
            print(f"Erro: Pasta que começa com '{nome_produto}' não encontrada.")
            return

        # Função para encontrar a janela do popup de seleção
        def find_popup_window():
            def enum_callback(hwnd, result):
                if win32gui.IsWindowVisible(hwnd) and "Abrir" in win32gui.GetWindowText(hwnd):
                    result.append(hwnd)
            popups = []
            win32gui.EnumWindows(enum_callback, popups)
            return popups[0] if popups else None

        # Espera o popup abrir
        time.sleep(2)

        # Tentar focar na janela do popup
        hwnd = find_popup_window()
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            print("Popup de seleção focado com sucesso.")
        else:
            print("Erro: Popup de seleção não encontrado.")
            return

        # Digitar o caminho completo da pasta do produto
        pyautogui.write(pasta_produto)
        pyautogui.press("enter")
        time.sleep(2)

        # Move o mouse para a posição e clica
        pyautogui.moveTo(590, 360, duration=0.5)
        pyautogui.click()
        print(f"Clique realizado na posição X={590}, Y={360}.")

        # Selecionar todos os arquivos da pasta
        pyautogui.hotkey("ctrl", "a")
        time.sleep(2)

        # Confirmar a seleção
        pyautogui.press("enter")
        print(f"Imagens da pasta '{os.path.basename(pasta_produto)}' enviadas com sucesso!")
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao enviar imagens: {e}")


def extrair_dados_loja():
    diretorio_base = os.path.join(os.getcwd(), "loja")
    dados_produtos = []

    # Padrão ajustado para capturar até "REF", "_" ou o final da linha
    padrao_nome = r"Nome:\s*(.+?)(?:\s+REF|\s+_|$)"
    padrao_sku = r"SKU:\s*SKU\s*([A-Za-z0-9\-]+)"
    padrao_preco_normal = r"Preço Normal:\s*R\$\s*([\d\.,]+)"
    padrao_preco_desconto = r"Preço com Desconto:\s*(.+)"

    if not os.path.isdir(diretorio_base):
        print(f"Erro: A pasta '{diretorio_base}' não foi encontrada.")
        return []

    for root, dirs, files in os.walk(diretorio_base):
        if "info.txt" in files:
            caminho_arquivo = os.path.join(root, "info.txt")

            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                    nome = re.search(padrao_nome, conteudo)
                    sku = re.search(padrao_sku, conteudo)
                    preco_normal = re.search(padrao_preco_normal, conteudo)
                    preco_desconto = re.search(padrao_preco_desconto, conteudo)

                    # Tratamento do nome: separar e juntar sem a última posição
                    if nome:
                        nome = nome.group(1)
                        nome_partes = nome.split()
                        nome = " ".join(nome_partes[:-1])  # Junta sem a última parte
                    else:
                        nome = conteudo.strip()  # Retorna o texto completo se não encontrar o padrão

                    # Tratamento do SKU: separar e pegar a última posição
                    if sku:
                        sku = sku.group(1)
                        sku = sku.split()[-1]  # Pega apenas a última parte
                    else:
                        sku = conteudo.strip()  # Retorna o texto completo se não encontrar o padrão

                    preco_normal = preco_normal.group(1) if preco_normal else "N/A"
                    preco_desconto = preco_desconto.group(1) if preco_desconto else "N/A"

                    imagens = [os.path.join(root, file) for file in files if file.lower().endswith(('.jpg', '.png', '.jpeg'))]

                    dados_produtos.append({
                        "nome": nome,
                        "sku": sku,
                        "preco_normal": preco_normal,
                        "preco_desconto": preco_desconto,
                        "imagens": imagens
                    })
            except Exception as e:
                print(f"Erro ao ler o arquivo 'info.txt' na pasta '{os.path.basename(root)}': {e}")

    return dados_produtos

def preencher_formulario(driver, wait, produto):
    actions = ActionChains(driver)
    texto = """
        Características: Tecido firme, com elasticidade, não apresenta transparência.
        Não da bolinhas nem desbota.
        Modelagem: Ampla e personalizada, se adapta facilmente ao corpo.
        Produto de Excelente qualidade.

        DÚVIDAS FREQUENTES:

        (Por favor leia, escrevemos com muito carinho e temos certeza que irá te ajudar)
        1) O produto é o mesmo da foto?
        O produto é o mesmo da foto, o tecido, a modelagem, o corte... Porém por ser uma foto sempre poderá haver variações do produto real.
        2) As cores claras são transparentes?
        A peça não apresenta transparência.
        3) Possui bojo?
        Esse modelinho não acompanha bojo, pois o mesmo comprometeria o conforto da peça.
        4) Se eu não gostar ou não servir, posso trocar ou devolver?
        A troca por tamanho ou insatisfação, deverá ser realizada no prazo de 7 dias corridos após o recebimento.
        5) O tecido estica?
        O tecido possui bastante elastano o que gera uma ótima elasticidade a peça.
        6) Após a aprovação do pagamento em quanto tempo o pedido é enviado?     
        Normalmente todos os pedidos são postados no mesmo dia da compra ou no máximo no próximo dia útil."""
    try:
        # Clica no botão "Incluir Produto"
        botao_incluir = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'nimbus--button.nimbus--button--primary')))
        botao_incluir.click()

        print(f"Enviando produto: {produto['nome']}")

        time.sleep(2)

        # Preencher o campo de nome
        nome = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[2]/div[1]/div[2]/div/div/div/div[1]/div/input')))
        actions.move_to_element(nome).click().perform()
        nome.clear()
        nome.send_keys(produto["nome"])

        time.sleep(2)

        # Preencher o campo dscrição
        # Move o mouse para a posição e clica
        pyautogui.moveTo(895, 822, duration=0.5)
        pyautogui.click()
        print(f"Clique realizado na posição X={895}, Y={822}.")

        # cola texto na area
        copiar_para_area_transferencia(texto)
        pyautogui.hotkey("ctrl", "v")

        time.sleep(2)

        # Clicar no botão de upload para abrir o popup Upload das imagens
        botao_upload = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[2]/div[2]/div[2]/div/div[1]/section/div/label')))
        botao_upload.click()
        
        # Chamar a função de upload das imagens
        upload_imagens(produto["nome"])

        time.sleep(2)

        # Preencher preço normal
        preco_normal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_price"]')))
        actions.move_to_element(preco_normal).click().perform()
        preco_normal.clear()
        preco_normal.send_keys(2*float(produto["preco_normal"].replace(" R$ ", "").replace(",", ".")))

        time.sleep(2)

        # Preencher preço com desconto, se houver
        if produto["preco_desconto"].lower() != "sem desconto":
            preco_desconto = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_promotionalPrice"]')))
            actions.move_to_element(preco_desconto).click().perform()
            preco_desconto.clear()
            preco_desconto.send_keys(2*float(produto["preco_desconto"].replace(" R$ ", "").replace(",", ".")))
            time.sleep(2)

        # Preencher o SKU
        sku = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_sku"]')))
        actions.move_to_element(sku).click().perform()
        sku.clear()
        sku.send_keys(produto["sku"])

        time.sleep(2)

        # Preencher o peso
        peso = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[2]/div[7]/div/div[2]/div/div[1]/div[2]/div/div/div[1]/div/div/input')))
        actions.move_to_element(peso).click().perform()
        peso.clear()
        peso.send_keys("0.200")

        # Preencher o comprimento
        comprimento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_depth"]')))
        actions.move_to_element(comprimento).click().perform()
        comprimento.clear()
        comprimento.send_keys("30")

        # Preencher o largura
        largura = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_width"]')))
        actions.move_to_element(largura).click().perform()
        largura.clear()
        largura.send_keys("30")

        # Preencher o altura
        altura = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input_height"]')))
        actions.move_to_element(altura).click().perform()
        altura.clear()
        altura.send_keys("10")


        time.sleep(2)

        # Preencher categoria
        abrir_cat = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[2]/div[9]/div[2]/a')))
        actions.move_to_element(abrir_cat).click().perform()
        print("Abrindo categorias...")
        time.sleep(2)

        categorias = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'nimbus--interactive-list-item__block')))
        check_box = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'nimbus--checkbox-wrapper')))
        print(f"Total de categorias encontradas: {len(categorias)}")
        print(f"Total de checkboxes encontrados: {len(check_box)}")
        
        for i ,categoria in enumerate(categorias):
            categoria_nome = categoria.find_element(By.XPATH, ".//p")
            nomecat = categoria_nome.text
            print(f"Categoria: {nomecat}")

            if nomecat in produto["nome"]:
                categoria.click()
                pyautogui.moveTo(895, 822, duration=0.5)
                pyautogui.click()
                time.sleep(2)
                break
        
        time.sleep(2)
        
        # Preencher tamanhos
        variacoes = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[2]/div[10]/div[2]/div/a')))
        actions.move_to_element(variacoes).click().perform()
        time.sleep(2)
        tamanho = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'nimbus-select_appearance_neutral__1xzshar3.nimbus-select_base__1xzshar2')))
        tamanho.click()
        time.sleep(2)
        tamanhos = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id-select"]/option[3]')))
        tamanhos.click()
        time.sleep(2)
        tamanho_chckbox = driver.find_elements(By.CLASS_NAME, 'nimbus--checkbox-wrapper')
        for i in range(0, 5):
            tamanho_chckbox[i].click()
        btn_salvar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'nimbus--link.nimbus--link--secondary.nimbus--link--base')))
        btn_salvar.click()
        pyautogui.moveTo(590, 360, duration=0.5)
        pyautogui.click()

        time.sleep(2)

        # Enviar o formulário
        btn_enviar = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div/div/form/div/div[3]/div[2]/button')))
        actions.move_to_element(btn_enviar).click().perform()

        time.sleep(5)

        print(f"Produto '{produto['nome']}' enviado com sucesso!\n")

    except Exception as e:
        print(f"Erro ao enviar o produto '{produto['nome']}': {e}")

# Setup do WebDriver
driver, wait = webdriver_setup()
actions = ActionChains(driver)

# Acessa a página de login
url = "https://bemotion2.lojavirtualnuvem.com.br/admin/v2/products?page=1&sortBy=created-at-descending"
driver.get(url)
time.sleep(5)

# Login
driver.find_element(By.XPATH, '//*[@id="user-mail"]').send_keys(os.getenv("login"))
driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys(os.getenv("senha"))
driver.find_element(By.XPATH, '//*[@id="register-page"]/div/div/div[2]/div[1]/div[3]/form/div[4]/p[2]/input').click()
time.sleep(5)

# Extração dos produtos e envio
produtos = extrair_dados_loja()
for produto in produtos:
    driver.refresh()
    time.sleep(5)
    preencher_formulario(driver, wait, produto)
    time.sleep(2)
    btn_voltar = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="back-navigation-topbar"]/button')))
    btn_voltar.click()
    time.sleep(5)

driver.quit()
