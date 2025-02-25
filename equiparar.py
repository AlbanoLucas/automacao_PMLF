from imports import *
from webdriver_setup import webdriver_setup


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
def equiparar():
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

