from imports import *
from webdriver_setup import webdriver_setup
from read_xls import carregar_dados


def equiparar():
    driver, wait = webdriver_setup()
    ###################################  EQUIPARAR  ###################################
    #Botao Pesquisar
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mostrarBotaoBusca"]/input'))).click()

    #Pesquisa Nome
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="layerBusca"]/table/tbody/tr[3]/td[2]/input'))).send_keys("Albano Lucas Evangelista de Souza")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="layerBusca"]/table/tbody/tr[7]/td[1]/input[1]'))).click()

    #Seleciona Usuario
    wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table[3]/tbody/tr[2]/td[2]/a'))).click()
    perfis = driver.find_element(By.ID, 'perfisId')
    atribuicoes = perfis.find_elements(By.TAG_NAME, 'option')
    lista_atribuicoes = []
    for atribuicao in atribuicoes:
        lista_atribuicoes.append(atribuicao.text)
    driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table/tbody/tr[3]/td/input[2]')
    return lista_atribuicoes

def cadastro(dados_completos):
    for dado in dados_completos:

        nome_completo = dado.get('nome')
        secretaria = dado.get('secretaria')
        setor = dado.get('setor')
        departamento = dado.get('departamento')
        divisao = dado.get('divisao')
        matricula = dado.get('matricula')
        atribuicoes = dado.get('atribuicoes', [])
        login_name = dado.get('login')
        senha = dado.get('senha')
        cargo = dado.get('cargo')

        driver, wait = webdriver_setup()
        url = "https://lfrh.metropolisweb.com.br/metropolisWEB/"
        driver.get(url)
        time.sleep(5)
     
       #Login Acesso
        login = wait.until(EC.visibility_of_element_located((By.ID, 'campoLogin')))
        login.send_keys("alsouza")
        #Senha Acesso
        password = wait.until(EC.visibility_of_element_located((By.ID, 'campoSenha')))
        password.send_keys("025014")
        #Entrar
        button_login = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'button_form')))
        button_login.click()
        time.sleep(2)
        pyautogui.press('enter')
        # Abrir Pagina dos Usuarios
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSeguranca"]/td[2]'))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSegurancaControle"]/td[2]'))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divSGnivelControle"]/table/tbody/tr[2]/td/a'))).click()

        if  != None:
            atribuicoes = equiparar()
        #Botao Incluir
        includ_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table[2]/tbody/tr/td[1]/input[2]')))
        includ_button.click()
        time.sleep(2)

        try:
            #PESSOA FISICA
            #Pesquisa PF    
            individual_search = wait.until(EC.visibility_of_element_located((By.ID, 'pesquisarNome')))
            individual_search.click()
            time.sleep(2)
            # Alterna Janela Navegador
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
        departamento_element.send_keys(departamento)
        time.sleep(2)
        divisao_element = driver.find_element(By.ID, 'unidadeOrganizacionalNivel4Id')
        divisao_element.send_keys(divisao)
        time.sleep(2)
        #Botao OK
        driver.find_element(By.XPATH, '//*[@id="auxiliar_footer"]/div[3]').click()   

        #STATUS
        driver.find_element(By.ID, 'cgValorDominioByStatusId.valorDominioId').send_keys('Ativo')
        
        #LOGIN NAME
        login_element = driver.find_element(By.ID, 'user')
        login_element.send_keys(login_name)
        #SENHA
        senha_element = driver.find_element(By.ID, 'pass')
        senha_element.send_keys(senha)

        #MATRICULA
        matricula_element = driver.find_element(By.ID, 'numMatricula')
        matricula_element.send_keys(matricula)

        #CARGO
        cargo_element = driver.find_element(By.ID, 'cargoId')
        cargo_element.send_keys(cargo)

        #ATRIBUICOES
        for atribuicao in atribuicoes:
            atribuicoes_element = driver.find_element(By.ID, 'perfilId')
            atribuicoes_element.send_keys(atribuicao)
            driver.find_element(By.XPATH, '//*[@id="aba1"]/fieldset/table/tbody/tr[11]/td/fieldset/strong/input[1]').click()
            time.sleep(1)

        time.sleep(1000000)
        #Botao Salvar
        # driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table/tbody/tr[3]/td/input[2]').click() ##################################



dados_completos = carregar_dados()
cadastro(dados_completos)