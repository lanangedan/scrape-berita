import time
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging untuk debug
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load CSV Data dengan pengecekan
csv_file = "removal_urls.csv"  # Sesuaikan dengan lokasi file CSV
try:
    data = pd.read_csv(csv_file)
    if data.empty:
        logging.error("❌ File CSV kosong. Harap isi dengan URL yang ingin dihapus.")
        exit()
except FileNotFoundError:
    logging.error(f"❌ File {csv_file} tidak ditemukan. Pastikan file ada di folder yang benar.")
    exit()

# Setup WebDriver dengan profil Chrome yang sudah login
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")  # Mengatasi error DEPRECATED_ENDPOINT
chrome_options.add_argument("--disable-notifications")  # Mencegah notifikasi Chrome
chrome_options.add_argument(r"--user-data-dir=C:\Users\Lanang Legion\AppData\Local\Google\Chrome\User Data")
chrome_options.add_argument("--profile-directory=Profile 32")

# Mulai WebDriver dengan handling error
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Buka Google Search Console Removal Tool
    logging.info("Membuka Google Search Console Removals")
    driver.get("https://search.google.com/search-console/removals")

    # Tunggu halaman terbuka sepenuhnya
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

except Exception as e:
    logging.error(f"❌ Gagal membuka browser atau halaman: {e}")
    exit()

# Loop setiap URL untuk diajukan permintaan removal
for index, row in data.iterrows():
    url_to_remove = row["url"]  # Ambil URL dari CSV
    logging.info(f"Mengajukan removal untuk: {url_to_remove}")

    try:
        # Tutup pop-up jika ada
        try:
            close_popup = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))
            )
            close_popup.click()
            logging.info("✅ Pop-up berhasil ditutup.")
        except:
            logging.info("⚠️ Tidak ada pop-up yang menghalangi.")

        # Klik tombol "New Request"
        new_request_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/c-wiz[3]/div/div[2]/div/div/div/div/div[2]/span[1]/div/div/div/div[1]/div/div[2]/div"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", new_request_btn)
        time.sleep(1)
        try:
            new_request_btn.click()
        except:
            driver.execute_script("arguments[0].click();", new_request_btn)
        time.sleep(2)

        # Masukkan URL
        url_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/span/div/div/div[2]/span[1]/div[2]/label/input"))
        )
        url_input.send_keys(url_to_remove)
        time.sleep(1)

        # Pilih radio button "Remove all URLs with this prefix"
        prefix_radio = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/span/div/div/div[2]/span[1]/div[3]/span/label[2]/div"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", prefix_radio)
        time.sleep(1)
        try:
            prefix_radio.click()
        except:
            driver.execute_script("arguments[0].click();", prefix_radio)
        time.sleep(1)

        # Klik "Next"
        next_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/div[3]/div[2]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", next_btn)
        time.sleep(1)
        try:
            next_btn.click()
        except:
            driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(2)

        # Klik "Submit Request"
        submit_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/div[3]/div[2]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
        time.sleep(1)
        try:
            submit_btn.click()
        except:
            driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)

        logging.info(f"✅ Berhasil mengajukan removal untuk: {url_to_remove}")

    except Exception as e:
        logging.error(f"❌ Gagal mengajukan removal untuk {url_to_remove}: {e}")
        continue  # Lewati URL ini jika gagal, lanjutkan ke berikutnya

# Tutup browser setelah selesai
logging.info("Menutup browser")
driver.quit()
