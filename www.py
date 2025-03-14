from imports import *

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

# Espera até o Angular concluir o processamento
# wait.until(lambda driver: driver.execute_script("return window.angular !== undefined && window.angular.element(document).injector() !== undefined"))

app_root = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "body > app-root"))
)
app_home = app_root.find_element(By.CSS_SELECTOR, 'body > app-root > app-homepage')
app_ed_ant = app_home.find_element(By.CSS_SELECTOR, 'body > app-root > app-homepage > app-edicoes-anteriores')
tabela_elements = app_ed_ant.find_elements(By.TAG_NAME, 'tr')
for linha in tabela_elements:
    linha_elements = linha.find_elements(By.TAG_NAME, 'td')
    if linha_elements[0].text == data_atual:
        edicoes.append(linha_elements[1].text)
    else:
        break
print(edicoes)