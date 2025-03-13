from imports import *
from ngwebdriver import NgWebDriver

edicoes = []
data_atual = datetime.now().strftime('%d/%m/%Y')
url = "https://laurodefreitas.ba.gov.br/2022/"
chrome_options = Options()
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20, poll_frequency=2)
driver.get(url)
time.sleep(2)
driver.find_element(By.XPATH, '/html/body/header/div/div/div[1]/div/div/div/div[2]/a[2]/button').click()
time.sleep(10)
app_ed_ant = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-homepage/app-edicoes-anteriores')))
tabela_elements = app_ed_ant.find_elements(By.TAG_NAME, 'tr')
for linha in tabela_elements:
    linha_elements = linha.find_elements(By.TAG_NAME, 'td')
    if linha_elements[0].text == data_atual:
        edicoes.append(linha_elements[1].text)
    else:
        break
print(edicoes)