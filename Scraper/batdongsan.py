from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
# Setup ChromeDriver
options = webdriver.ChromeOptions()
# options.add_argument('--disable-blink-features=AutomationControlled')  # Disable automation flags
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option(
        "prefs", {
            # block image loading
            "profile.managed_default_content_settings.images": 2,
        }
    )
# options.add_argument('--headless')  # Uncomment for headless mode

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)
# List to store scraped data for all cards
data_list = []
STANDARD_KEYS = ['Diện tích', 'Mức giá', 
                 'Số phòng ngủ', 'Số toilet','Số tầng']

def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))


def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    human_like_delay(1, 3)

def scrape_page():

    data = {}
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 're__pr-specs-content-item-value')))
        
        specs_items = driver.find_elements(By.CSS_SELECTOR, '.re__pr-specs-content-item')

        for item in specs_items:
                    title_element = item.find_element(By.CLASS_NAME, 're__pr-specs-content-item-title')
                    value_element = item.find_element(By.CLASS_NAME, 're__pr-specs-content-item-value')

                    title = title_element.text.strip()
                    value = value_element.text.strip()

                    data[title] = value


        for key in STANDARD_KEYS:
            if key not in data:
                data[key] = None
        print(data)
        data_list.append(data)
    except TimeoutException:
        print("Timeout reached while trying to load the card page.")

def scrape_main_page(url):
    driver.get(url)
    scroll_to_bottom()
    human_like_delay(2,4)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'js__product-link-for-product-id')))
    # remove_unwanted_div()
    cards = driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')

    for i in range(len(cards)-2):
        try:
            print(len(cards))
            print(f"Clicking on card {i + 1}...")
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'js__product-link-for-product-id')))
            # remove_unwanted_div()
            # close_popup()
            cards = driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')
            # remove_search_form()
            human_like_delay(2,3)

            driver.execute_script("arguments[0].scrollIntoView();", cards[i])
            human_like_delay(1, 2)
            cards[i].click()

            human_like_delay(1, 3)

            scrape_page()
            
            human_like_delay(2, 5)

        except Exception as e:
            print(f"An error occurred while clicking on card {i + 1}: {e}")
        finally:
            try:
                driver.back()
            except:
                driver.get(url) 

# Start scraping the main page
try:
    for i in range(5,152):
        try:
            url = 'https://guland.vn/mua-ban-nha-mat-pho-mat-tien-da-nang'
            scrape_main_page(url)
        except:
            break
except Exception:
    print("An error occurred while scraping the main page.")
finally:
    print(data_list)
    df = pd.DataFrame(data_list)
    df.to_csv('scraped_data_only_gianha_2.csv',encoding="utf-8", index=False)
    print("Saved successfully")
driver.quit()
