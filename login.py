from imports import *
from webdriver_setup import webdriver_setup

def login():
    driver, wait = webdriver_setup()
    url = "https://lfrh.metropolisweb.com.br/metropolisWEB/"
    driver.get(url)
    time.sleep(5)

    nome_completo = "Albano Lucas Evangelista de Souza"
    secretaria = "Secretaria de Administração"
    setor = "DTIC"
    cpf = '02501454561'



    #LOGIN
    login = wait.until(EC.visibility_of_element_located((By.ID, 'campoLogin')))
    login.send_keys("alsouza")
    #SENHA
    password = wait.until(EC.visibility_of_element_located((By.ID, 'campoSenha')))
    password.send_keys("025014")
    #ENTRAR
    button_login = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'button_form')))
    button_login.click()
    time.sleep(2)
    pyautogui.press('enter')
    # BRIR PAGINA DOS USUARIOS
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSeguranca"]/td[2]'))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSegurancaControle"]/td[2]'))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divSGnivelControle"]/table/tbody/tr[2]/td/a'))).click()
    #BOTAO INCLUIR
    includ_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table[2]/tbody/tr/td[1]/input[2]')))
    includ_button.click()
    time.sleep(2)

    try:
        #PESSOA FISICA
        #PESQUISA PF    
        individual_search = wait.until(EC.visibility_of_element_located((By.ID, 'pesquisarNome')))
        individual_search.click()
        time.sleep(2)
        # ALTERNA JANELA NAVEGADOR
        windows = driver.window_handles
        driver.switch_to.window(windows[1])
        name_element = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/table[1]/tbody/tr[2]/td[2]/input')
        name_element.send_keys(nome_completo) #SUBSTITUR POR POR VARIAVEL
        search_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[1]/tbody/tr[5]/td/input[1]')))
        search_button.click()
        time.sleep(2)
        radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[4]/tbody/tr[2]/td[1]/input')))
        radio_button.click()
        time.sleep(2)
        select_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[3]/tbody/tr/td/input[1]')))
        select_button.click()
        driver.close()
        driver.switch_to.window(windows[0])
        time.sleep(2)
    except:
        print("Erro ao selecionar pessoa física")

    #UNIDADE ORGANIZACIONAL
    driver.find_element(By.ID, 'seleciona-uo').click()
    time.sleep(2)
    secretaria_element = driver.find_element(By.ID, 'unidadeOrganizacionalNivel1Id')
    secretaria_element.send_keys(secretaria)
    time.sleep(2)
    setor_element = driver.find_element(By.ID, 'unidadeOrganizacionalNivel2Id')
    setor_element.send_keys(setor)
    time.sleep(2)
    departamento_element = driver.find_element(By.ID, 'unidadeOrganizacionalNivel3Id')
    time.sleep(2)
    divisao_element = driver.find_element(By.ID, 'unidadeOrganizacionalNivel4Id')
    time.sleep(2)
    #BOTAO OK
    driver.find_element(By.XPATH, '//*[@id="auxiliar_footer"]/div[3]').click()   

    #STATUS
    driver.find_element(By.ID, 'cgValorDominioByStatusId.valorDominioId').send_keys('Ativo')
    try:
        #TRATAMENTO DE NOME
        nome = nome_completo.split()

        # Caso o nome tenha apenas nome e sobrenome
        if len(nome) == 2:
            primeiro_nome = nome[0][0].lower()  # Primeira letra do primeiro nome em minúsculo
            segundo_nome = nome[1].lower()  # Segundo nome em minúsculas
            return f"{primeiro_nome}{segundo_nome}"

        # Caso o nome tenha mais de 2 partes
        else :
            primeiro_nome = nome[0][0].lower()  # Primeira letra do primeiro nome em minúsculo
            segundo_nome = nome[1][0].lower() if len(nome) > 1 else ""  # Primeira letra do segundo nome, se existir
            ultimo_nome = nome[-1].lower()  # Último nome em minúsculas
            login_name = f"{primeiro_nome}{segundo_nome}{ultimo_nome}"
    except:
        print("Erro ao gerar login name")
    
    #LOGIN NAME
    login_element = driver.find_element(By.ID, 'user')
    login_element.send_keys(login_name)
    #SENHA
    senha_element = driver.find_element(By.ID, 'pass')
    senha_element.send_keys(cpf[:6])

    #MATRICULA
    matricula_element = driver.find_element(By.ID, 'numMatricula')

    
    
    time.sleep(15)
	
login()