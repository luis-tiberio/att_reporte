from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime
import subprocess
import os
from PIL import Image
from PIL import ImageGrab
import pygetwindow as gw
import pyautogui
import pytz

timezone = pytz.timezone('America/Sao_Paulo')

# Diretório de download para GitHub Actions
download_dir = "/tmp"

# Cria o diretório, se não existir
os.makedirs(download_dir, exist_ok=True)

# Configurações do Chrome para ambiente headless do GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Configurações de download
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Inicializa o driver
driver = webdriver.Chrome(options=chrome_options)

def login(driver):
    driver.get("https://spx.shopee.com.br/")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Ops ID"]')))
        driver.find_element(By.XPATH, '//*[@placeholder="Ops ID"]').send_keys('Ops34139')
        driver.find_element(By.XPATH, '//*[@placeholder="Senha"]').send_keys('@Shopee1234')
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button'))
        ).click()

        time.sleep(15)
        try:
            popup = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ssc-dialog-close"))
            )
            popup.click()
        except:
            print("Nenhum pop-up foi encontrado.")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    except Exception as e:
        print(f"Erro no login: {e}")
        driver.quit()
        raise

def get_data(driver):
    data = []
    try:
        # Coletar dados do primeiro link
        driver.get("https://spx.shopee.com.br/#/dashboard/facility-soc/historical-data")
        WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mgmt-dashboard-content"]')))
        first_value = driver.find_element(By.XPATH, '//*[@id="mgmt-dashboard-content"]/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/table/tbody/tr[2]/td[25]').text
        data.append(first_value)

        # Coletar dados do segundo link
        driver.get("https://spx.shopee.com.br/#/dashboard/toProductivity?page_type=Outbound")
        time.sleep(10)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div')))
        second_value = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div').text
        data.append(second_value)

        # Acessar o XPath do terceiro dado
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/div/div/div/div/div[3]').click()
        time.sleep(10)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div')))
        third_value = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div').text
        data.append(third_value)

        # Acessar o XPath do quarto dado
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/div/div/div/div/div[4]').click()
        time.sleep(10)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div')))
        time.sleep(20)
        fourth_value = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div/div/div/table/thead/tr[2]/th[4]/div/div').text
        data.append(fourth_value)
      
    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        driver.quit()
        raise
    return data

def update_google_sheets(data):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1_lmuTCD1-PX4S4a-M4TAVHoQ4r_X5C1ZssXdJhc80bA/edit?gid=0#gid=0').worksheet("Python")

    current_time = datetime.datetime.now(timezone)
    if 7 <= current_time.hour <= 23:
        row_number = current_time.hour - 5
    elif current_time.hour == 0:
        row_number = 19
    elif 1 <= current_time.hour <= 5:
        row_number = current_time.hour + 19
    else:
        print(f"Hora fora do intervalo programado: {current_time.hour}:{current_time.minute}")
        return

    if 2 <= row_number <= 25:
        cell_range = f'B{row_number}:F{row_number}'
        values = [data]
        sheet.update(cell_range, values)
        print(f"Dados atualizados na linha {row_number} ({cell_range})")
    else:
        print(f"Hora inválida para atualização: {current_time.hour}:{current_time.minute}")

def main():
    try:
        login(driver)
        data = get_data(driver)
        update_google_sheets(data)
        print("Dados atualizados com sucesso.")

    except Exception as e:
        print(f"Erro durante o processo: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
