from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
STANDARD_KEYS = ['Diện tích', 'Mức giá', 'Mặt tiền', 'Đường vào', 'Hướng nhà', 'Hướng ban công', 
                 'Số phòng ngủ', 'Số toilet', 'Pháp lý', 'Số tầng', 'Nội thất','Longitude','Latitude']
def remove_unwanted_div():
    script = """
    var element = document.querySelector('.re__listing-verified-similar-v2.js__listing-verified-similar');
    if (element) {
        element.remove();
    }
    """
    driver.execute_script(script)
    print("Ad removed.")
def remove_search_form():
    script = """
    var element = document.querySelector('#boxSearchForm');
    if (element) {
        element.remove();
    }
    """
    driver.execute_script(script)
    print("Search form removed.")
# Human-like delay function
def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))
def close_popup():
    # Attempt to detect and close pop-ups if any exist
    try:
        popup_close_button = driver.find_element(By.CSS_SELECTOR, '.nomodal')  # Example selector for pop-up
        driver.execute_script("""
            var element = document.querySelector('.nomodal');
            if (element) {
                element.remove();
            }
        """)
        print("Popup closed.")
    except NoSuchElementException:
        print("No popup found.")
    except Exception as e:
        print(f"An error occurred while closing the popup: {e}")
def extract_latitude_longitude():
    try:
        # Wait for the iframe to load
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[data-src]')))
        
        # Get the data-src attribute
        data_src = iframe.get_attribute('data-src')
        print(f"Data source URL: {data_src}")
        
        # Use regex to extract the latitude and longitude from the URL
        pattern = r"q=([\d.]+),([\d.]+)&"
        match = re.search(pattern, data_src)
        
        if match:
            latitude = match.group(1)
            longitude = match.group(2)
            print(f"Latitude: {latitude}, Longitude: {longitude}")
            return latitude, longitude
        else:
            print("Latitude and Longitude not found in the URL.")
            return None, None
    except Exception as e:
        print(f"Error extracting latitude and longitude: {e}")
        return None, None

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

        latitude, longitude = extract_latitude_longitude()
        if latitude and longitude:
            data['Latitude'] = latitude
            data['Longitude'] = longitude
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
    remove_unwanted_div()
    cards = driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')

    for i in range(len(cards)-2):
        try:
            print(len(cards))
            print(f"Clicking on card {i + 1}...")
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'js__product-link-for-product-id')))
            remove_unwanted_div()
            close_popup()
            cards = driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')
            remove_search_form()
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
            if i ==1:
                url = 'https://batdongsan.com.vn/ban-loai-bat-dong-san-khac-da-nang?cIds=362'
            else:
                url = f'https://batdongsan.com.vn/ban-loai-bat-dong-san-khac-da-nang/p{i}?cIds=362'
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
