import time
import csv
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_driver():
    """Initialize the Chrome WebDriver with a specific profile."""
    options = Options()
    user_data_dir = r"C:\Users\Lanang Legion\AppData\Local\Google\Chrome\User Data"  # Main user data directory
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument("profile-directory=Profile 2")  # Specify the profile

    service = Service("C:/WebDriver/chromedriver.exe")  # Adjust the path to your ChromeDriver
    return webdriver.Chrome(service=service, options=options)

def scrape_linkedin_data(company_name, university):
    """Scrape data from LinkedIn."""
    driver = initialize_driver()
    
    try:
        # Open the LinkedIn page
        url = f"https://www.linkedin.com/company/{company_name}/people/"
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # Prompt user to scroll
        input("Please scroll through the page and press Enter when you're ready to scrape...")

        # Count the number of profiles
        profiles = driver.find_elements(By.CSS_SELECTOR, "li.org-people-profile-card__profile-card-spacing")
        logging.info(f"Total profiles found: {len(profiles)}")

        # Scrape data
        data_list = []

        for profile in profiles:
            try:
                name = profile.find_element(By.CSS_SELECTOR, "div.lt-line-clamp--single-line").text.strip()
                
                # Handle potential error when locating the link
                try:
                    link = profile.find_element(By.CSS_SELECTOR, "a.link-without-visited-state").get_attribute("href")
                    link = link.split('?')[0]  # Get the part before the '?'
                except Exception as e:
                    logging.error(f"Error scraping link for {name}: {e}")
                    link = "N/A"  # Default value if link is not found

                bio = profile.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle div.lt-line-clamp--multi-line").text.strip()
                clubs = driver.find_element(By.CSS_SELECTOR, "h1.org-top-card-summary__title").text.strip()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data_list.append([timestamp, name, clubs, university, bio, link])  # Adjusted order
                logging.info(f"✅ {name} added to CSV")
            except Exception as e:
                logging.error(f"Error scraping profile: {e}")

        # Save to CSV (append mode)
        csv_filename = "scrape_data_mahasiswa.csv"
        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';')
            if not file_exists:
                writer.writerow(["Timestamp", "Nama", "Organisasi", "Nama Institusi", "Biodata", "Link"])  # Write header if file is new
            writer.writerows(data_list)

        logging.info("✅ Scraping completed, data appended to CSV!")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        company_name = input("Enter the company name (after 'company/'): ")
        university = input("Enter the name of the university: ")
        scrape_linkedin_data(company_name, university)

        # Ask if the user wants to scrape another company
        another = input("Do you want to scrape another company? (y/n): ").strip().lower()
        if another != 'y':
            break
