import time
import csv
import os
import keyboard
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

total_records = 0  # Global counter untuk total berita yang di-scrape

def get_max_page(driver, url):
    driver.get(url + "&page=100")
    time.sleep(3)  # Jeda untuk menghindari block
    try:
        paging = driver.find_element(By.CSS_SELECTOR, ".paging")
        last_page = paging.find_elements(By.TAG_NAME, "a")[-1].text
        return int(last_page)
    except Exception:
        return 1

def initialize_csv(csv_filename):
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Tanggal Rilis", "Judul", "Deskripsi", "Link", "Timestamp"])

def scrape_page(driver, url, csv_filename):
    global total_records  # Menggunakan variabel global untuk menyimpan total berita
    driver.get(url)
    time.sleep(3)  # Jeda untuk loading
    articles = driver.find_elements(By.CSS_SELECTOR, ".list-berita article a")

    data_list = []
    for article in articles:
        if keyboard.is_pressed('ctrl+q'):
            print("\n🔴 Force close detected! Exiting...")
            print(f"✅ Scraping dihentikan! Total {total_records} berita berhasil diambil.")
            driver.quit()
            exit()
        
        try:
            date_element = article.find_element(By.CSS_SELECTOR, "span.date")
            category_element = date_element.find_element(By.CSS_SELECTOR, "span.category")
            date_text = date_element.text.replace(category_element.text, "").strip()
        except Exception:
            date_text = ""
        
        try:
            title = article.find_element(By.CSS_SELECTOR, "h2.title").text.strip()
        except Exception:
            title = ""
        
        try:
            description = article.find_element(By.CSS_SELECTOR, "span.box_text p").text.strip()
        except Exception:
            description = ""
        
        try:
            link = article.get_attribute("href")
        except Exception:
            link = ""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_list.append([date_text, title, description, link, timestamp])
    
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        print("📝 Store data ke CSV...")
        print(f"📄 {len(data_list)} berita ditemukan pada halaman ini.")
        writer.writerows(data_list)
        total_records += len(data_list)  # Perbarui total berita

def main():
    tag = input("Masukkan tag berita: ").strip()
    base_url = f"https://www.detik.com/tag/{tag}/?sortby=time&page="
    csv_filename = "scraped_berita.csv"
    
    initialize_csv(csv_filename)
    
    options = Options()
    options.add_argument("-headless")  # Mode headless untuk tidak menampilkan browser
    service = Service("C:/WebDriver/geckodriver.exe")  # Ganti dengan path geckodriver
    driver = webdriver.Firefox(service=service, options=options)
    
    max_page = get_max_page(driver, base_url)
    print("📢 Scraping sedang dijalankan...")
    print(f"Total halaman: {max_page}")
    
    for page in range(1, max_page + 1):
        print(f"Scraping halaman {page}...")
        if keyboard.is_pressed('ctrl+q'):
            print("\n🔴 Force close detected! Exiting...")
            driver.quit()
            exit()
        scrape_page(driver, base_url + str(page), csv_filename)
    
    driver.quit()
    print(f"✅ Scraping selesai! Total {total_records} berita berhasil diambil.")

if __name__ == "__main__":
    main()
