from imports import *
from webdriver_setup import webdriver_setup


def cadastro():
    #INICIALIZA PAGINA CADASTRO
    driver, wait = webdriver_setup()
    # BRIR PAGINA DOS USUARIOS
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSeguranca"]/td[2]'))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="abaSegurancaControle"]/td[2]'))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divSGnivelControle"]/table/tbody/tr[2]/td/a'))).click()
    #BOTAO INCLUIR
    includ_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[3]/form/table[2]/tbody/tr/td[1]/input[2]')))
    includ_button.click()
    #PESQUISA PESSOA FISICA
    individual_search = wait.until(EC.visibility_of_element_located((By.ID, 'pesquisarNome')))
    individual_search.click()
    name_element = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[1]/tbody/tr[2]/td[2]/input')))
    name_element.send_keys("Albano lucas evangelista de souza") #SUBSTITUR POR POR VARIAVEL
    search_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[1]/tbody/tr[5]/td/input[1]')))
    search_button.click()
    radio_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[4]/tbody/tr[2]/td[1]/input')))
    radio_button.click()
    select_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table[3]/tbody/tr/td/input[1]')))
    select_button.click()

