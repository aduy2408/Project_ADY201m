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

# Setup ChromeDriver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option(
    "prefs", {
        # block image loading
        "profile.managed_default_content_settings.images": 2,
    }
)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)
data_list = []
STANDARD_KEYS = ['price','area','Loại BDS:','Chiều ngang:','Chiều dài:','Số phòng ngủ:','Số phòng tắm:','Số tầng:', 'Số tầng:',
                 'Vị trí:','Hướng cửa chính:','Đường/hẻm vào rộng:','Loại đường:']
def human_like_delay(min_time=1, max_time=3):
    """Random sleep to mimic human interactions."""
    time.sleep(random.uniform(min_time, max_time))
def remove_header():
    """Remove the header with class 'sdb-hdr-n' from the page."""
    try:
        driver.execute_script("""
            var header = document.querySelector('.sdb-hdr-n');
            if (header) {
                header.remove();
            }
        """)
        print("Header element removed.")
    except Exception as e:
        print(f"Failed to remove header element: {e}")
def click_see_more(num_clicks):
    """Click 'Xem thêm' button a specific number of times to load more cards."""
    for _ in range(num_clicks):
        try:
            # Remove the obstructing element
            remove_header()
            
            # Ensure the button is visible and clickable
            see_more_button = driver.find_element(By.XPATH, '//*[@id="btn-load-more"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
            human_like_delay(1, 2)
            
            # Click the button
            see_more_button.click()
            human_like_delay(2, 4)  # Wait for new cards to load
            print("Clicked 'Xem thêm' button to load more cards.")
        except NoSuchElementException:
            print("No 'Xem thêm' button found or no more content to load.")
            break
        except Exception as e:
            print(f"Error while clicking 'Xem thêm': {e}")
            break

def scrape_page():
    """Scrape data from the detail page."""
    data = {}
    try:
        price = driver.find_element(By.CLASS_NAME, 'dtl-prc__sgl.dtl-prc__ttl').text.strip()
        area = driver.find_element(By.CLASS_NAME, 'dtl-prc__sgl.dtl-prc__dtc').text.strip()
        data['price'] = price
        data['area'] = area
        
        # Locate specification items
        specs_items = driver.find_elements(By.CLASS_NAME, 's-dtl-inf')
        for item in specs_items:
            try:
                title_element = item.find_element(By.CLASS_NAME, 's-dtl-inf__lbl')
                value_element = item.find_element(By.CLASS_NAME, 's-dtl-inf__val')
                title = title_element.text.strip()
                value = value_element.text.strip()
                data[title] = value
            except NoSuchElementException:
                continue

        # Fill missing keys with None
        for key in STANDARD_KEYS:
            if key not in data:
                data[key] = None

        print(data)
        data_list.append(data)
    except TimeoutException:
        print("Timeout reached while trying to load the card page.")
def scrape_main_page(url):
    driver.get(url)
    human_like_delay(2, 4)

    # Click "Xem thêm" several times to load all cards
    click_see_more(50)  # Adjust the number of clicks as necessary

    # Wait for all cards to be present
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'l-sdb-list__single')))
    cards = driver.find_elements(By.CLASS_NAME, 'l-sdb-list__single')
    print(f"Total number of cards loaded: {len(cards)}")

    for index, card in enumerate(cards):
        try:
            print(f"Clicking on card {index + 1}...")
            driver.execute_script("arguments[0].scrollIntoView();", card)
            human_like_delay(1, 2)

            # Click on the card
            image_link = card.find_element(By.CSS_SELECTOR, '.sdb-image-wrap')
            driver.execute_script("arguments[0].click();", image_link)
            human_like_delay(2, 4)

            # Extract information from the card's detail page
            scrape_page()

            # Go back to the main page
            driver.back()
            human_like_delay(2, 4)

            # Re-fetch the cards after going back, as the elements may have been refreshed
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'l-sdb-list__single')))
            cards = driver.find_elements(By.CLASS_NAME, 'l-sdb-list__single')
        except Exception as e:
            print(f"An error occurred while processing card {index + 1}: {e}")
            driver.get(url)  # Reload the main page if something goes wrong
            human_like_delay(2, 4)
            click_see_more(50)  # Re-click 'Xem thêm' to reload the state
            cards = driver.find_elements(By.CLASS_NAME, 'l-sdb-list__single')

# Start scraping the main page
try:
    url = 'https://guland.vn/mua-ban-nha-mat-pho-mat-tien-da-nang'  # Replace with your target URL
    scrape_main_page(url)
except Exception as e:
    print(f"An error occurred while scraping the main page: {e}")
finally:

    df = pd.DataFrame(data_list)
    df.to_csv('scraped_data_only_gianha_GULANG.csv',encoding="utf-8", index=False)
    print("Saved successfully")
    driver.quit()
