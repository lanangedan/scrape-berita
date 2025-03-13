import time
import csv
import os
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_csv(csv_filename):
    """Initialize the CSV file with headers if it doesn't exist."""
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["Timestamp", "Nama", "Organisasi", "Nama Institusi", "Biodata", "Link"])

def wait_for_element(driver, by, value):
    """Wait for an element to be present in the DOM."""
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))

def get_max_pages(driver):
    """Get the maximum number of pages to scrape."""
    try:
        ul_element = driver.find_element(By.CSS_SELECTOR, "ul.display-flex")
        return len(ul_element.find_elements(By.TAG_NAME, "li"))
    except Exception as e:
        logging.error(f"Error getting max pages: {e}")
        return 1

def scrape_profiles(driver, csv_filename, organisasi, institusi):
    """Scrape profiles from the LinkedIn page."""
    try:
        profiles = wait_for_element(driver, By.CSS_SELECTOR, "li.org-people-profile-card__profile-card-spacing")
        data_list = []
        
        for profile in profiles:
            try:
                name = profile.find_element(By.CSS_SELECTOR, "div.lt-line-clamp--single-line").text.strip()
                full_link = profile.find_element(By.CSS_SELECTOR, "a.link-without-visited-state").get_attribute("href")
                link = full_link.split('?')[0] if '?' in full_link else full_link
                biodata = profile.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle div.lt-line-clamp--multi-line").text.strip()
                
                if name and link:  # Validate data
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data_list.append([timestamp, name, organisasi, institusi, biodata, link])
                    logging.info(f"✅ {name} ditambahkan ke CSV")
            except Exception as e:
                logging.error(f"Error scraping profile: {e}")
        
        with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(data_list)
    except Exception as e:
        logging.error(f"Error in scrape_profiles: {e}")

def initialize_driver():
    """Initialize the Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    user_data_dir = os.path.expanduser("~") + "/AppData/Local/Google/Chrome/User Data"
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory=Default")
    
    service = Service("C:/WebDriver/chromedriver.exe")  # Adjust path as necessary
    return webdriver.Chrome(service=service, options=options)

def main():
    """Main function to execute the scraping process."""
    linkedin_path = input("Masukkan bagian URL LinkedIn setelah 'company/': ").strip()
    if not linkedin_path:
        logging.error("LinkedIn path cannot be empty.")
        return
    
    organisasi = input("Masukkan nama Club yang sedang di Scraping: ").strip()
    institusi = input("Masukkan nama Institusi yang sedang di Scraping: ").strip()
    
    url = f"https://www.linkedin.com/company/{linkedin_path}"
    csv_filename = input("Masukkan nama file CSV (default: scrape_data_mahasiswa.csv): ") or "scrape_data_mahasiswa.csv"
    
    initialize_csv(csv_filename)
    
    driver = initialize_driver()
    
    try:
        driver.get(url)
        logging.info("🔵 Silakan lakukan login atau aktivitas lain. Ketik 'y' untuk mulai scraping, 'n' untuk keluar.")
        
        while True:
            start = input("Ready to scrape? (y/n): ").strip().lower()
            if start == "y":
                break
            elif start == "n":
                logging.info("❌ Scraping dibatalkan.")
                return
        
        max_pages = get_max_pages(driver)
        logging.info(f"📄 Total halaman scraping: {max_pages}")
        
        for page in range(1, max_pages + 1):
            driver.get(f"{url}&page={page}")
            wait_for_element(driver, By.CSS_SELECTOR, "li.org-people-profile-card__profile-card-spacing")  # Wait for profiles to load
            scrape_profiles(driver, csv_filename, organisasi, institusi)
            time.sleep(random.uniform(2, 5))  # Random sleep to avoid being flagged
            
        logging.info("✅ Scraping selesai, data telah disimpan!")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
