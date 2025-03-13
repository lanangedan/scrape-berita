# Step 1: Scraping Google News
import time
import csv
import random
import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Fungsi untuk menangani force terminate (CTRL+C)
def signal_handler(sig, frame):
    print("\n❌ Force terminate diterima. Keluar dari program...")
    try:
        driver.quit()
    except:
        pass
    sys.exit(0)

# Tangkap sinyal CTRL+C
signal.signal(signal.SIGINT, signal_handler)

# Konfigurasi Selenium
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")  # Menghindari deteksi bot
options.add_argument("--disable-software-rasterizer")  # Hindari WebGL error
options.add_argument("--enable-unsafe-webgpu")  # Aktifkan WebGL jika diperlukan
options.add_argument("--disable-features=NetworkService")  # Hilangkan error API lama

# Fungsi untuk mendeteksi apakah selector adalah XPath atau CSS
def detect_selector_type(selector):
    if selector.startswith("//"):
        return By.XPATH
    return By.CSS_SELECTOR

# Jalankan driver
try:
    options.add_argument("--profile-directory=Profile 32")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com/search?q=\"game+lokal+buatan+indonesia\"&sca_esv=fd720482c30bdadb&rlz=1C1CHBF_enID991ID991&tbm=nws&sxsrf=AHTn8zpMlgu5XOUBDl6gUaDYQkiXvRRHqg:1741720778226&tbas=0&source=lnt&sa=X&ved=2ahUKEwi716LC34KMAxVnzTgGHa1IMboQpwV6BAgCEBM&biw=1519&bih=1252&dpr=1")
    time.sleep(random.uniform(5, 8))
except Exception as e:
    print(f"⚠️ Gagal menjalankan Chrome dengan profil, mencoba tanpa profil...\n{e}")
    options.arguments.clear()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_page():
    global title_by, link_by, desc_by
    news_data = []
    
    # Tunggu elemen muncul
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((title_by, title_selector)))
    articles = driver.find_elements(title_by, title_selector)
    print(f"✅ Ditemukan {len(articles)} artikel di halaman ini.")
    
    for article in articles:
        try:
            title = article.text
            link_element = article.find_element(link_by, link_selector)
            url = link_element.get_attribute("href")
            
            # Coba ambil deskripsi jika ada
            try:
                desc_element = article.find_element(desc_by, desc_selector)
                description = desc_element.text if desc_element else ""
            except:
                description = ""
            
            print(f"🔍 Judul: {title}\n🔗 Link: {url}\n📄 Deskripsi: {description}")
            news_data.append([title, url, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        except Exception as e:
            print(f"⚠️ Terjadi kesalahan saat mengambil data: {e}")
            continue
    return news_data

# Input selector untuk judul, link, dan deskripsi
default_title_selector = "//div[contains(@class, 'SoaBEf')]//a"
default_link_selector = "//a[@jsname='YKoRaf' and contains(@class, 'WlydOe')]"
default_desc_selector = "//div[contains(@class, 'GI74Re')]"

title_selector = input("Masukkan XPath atau CSS selector untuk judul berita: ") or default_title_selector
title_by = detect_selector_type(title_selector)

link_selector = input("Masukkan XPath atau CSS selector untuk link berita: ") or default_link_selector
link_by = detect_selector_type(link_selector)

desc_selector = input("Masukkan XPath atau CSS selector untuk deskripsi berita: ") or default_desc_selector
desc_by = detect_selector_type(desc_selector)

all_news = []
while True:
    all_news.extend(scrape_page())
    
    # Cek tombol next page dengan try-except
    try:
        next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@id='pnnext']")))
        print("➡️ Pindah ke halaman berikutnya...")
        next_button.click()
        time.sleep(random.uniform(5, 8))
    except:
        print("✅ Semua halaman telah berhasil di-scrape.")
        break

# Simpan ke CSV
csv_filename = "google_news_scraped.csv"
with open(csv_filename, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=';')
    if file.tell() == 0:
        writer.writerow(["Judul", "URL", "Deskripsi", "Timestamp"])
    writer.writerows(all_news)

driver.quit()
print(f"✅ Scraping selesai. Data ditambahkan ke {csv_filename}")
