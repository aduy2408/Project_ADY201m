from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException,ElementNotInteractableException
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
STANDARD_KEYS = ['price', 'area', 'Loại BDS:', 'Chiều ngang:', 'Chiều dài:', 'Số phòng ngủ:', 'Số phòng tắm:', 
                 'Số tầng:', 'Vị trí:', 'Hướng cửa chính:', 'Đường/hẻm vào rộng:', 'Loại đường:']

def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def remove_header():
    try:
        driver.execute_script("""
            var header = document.querySelector('.sdb-hdr-n');
            if (header) {
                header.remove();
            }
        """)
        print("Header element removed.")
    except Exception as e:
        print(f"Failed to remove {e}")

def click_see_more(num_clicks):
    for _ in range(num_clicks):
        try:
            remove_header()
            
            see_more_button = driver.find_element(By.XPATH, '//*[@id="btn-load-more"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
            human_like_delay(1, 2)
            
            see_more_button.click()
            human_like_delay(2, 4) 
            print("Clicked to load more cards.")
        except NoSuchElementException:
            print("No button found or no more content to load.")
            break
        except Exception as e:
            print(f"Error while clicking: {e}")
            break

def scrape_page():
    data = {}
    try:
        price = driver.find_element(By.CLASS_NAME, 'dtl-prc__sgl.dtl-prc__ttl').text.strip()
        area = driver.find_element(By.CLASS_NAME, 'dtl-prc__sgl.dtl-prc__dtc').text.strip()
        data['price'] = price
        data['area'] = area
        
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

        for key in STANDARD_KEYS:
            if key not in data:
                data[key] = None

        print(data)
        data_list.append(data)
    except TimeoutException:
        print("Timeout reached while trying to load the card page.")

def collect_card_links(url):
    driver.get(url)
    human_like_delay(2, 4)

    # ADJUST    HERE
    click_see_more(2)  

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'l-sdb-list__single')))
    cards = driver.find_elements(By.CLASS_NAME, 'l-sdb-list__single')
    print(f"Total number of cards loaded: {len(cards)}")

    card_links = []
    for index, card in enumerate(cards):
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", card)
            human_like_delay(1, 2)
            
            try:
                link_element = card.find_element(By.CSS_SELECTOR, '.sdb-image-wrap')
                link = link_element.get_attribute('href')
            except NoSuchElementException:
                link_element = card.find_element(By.CSS_SELECTOR, '.c-sdb-card__tle a')
                link = link_element.get_attribute('href')

            if link:
                card_links.append(link)
                print(f"Collected link for card {index + 1}: {link}")
            else:
                print(f"No href found for card {index + 1}.")
        except TimeoutException:
            print(f"Timeout: Link not found for card {index + 1}.")
        except NoSuchElementException:
            print(f"Link not found for card {index + 1}.")
        except ElementNotInteractableException:
            print(f"Element not interactable for card {index + 1}.")
        except Exception as e:
            print(f"An error occurred while collecting link for card {index + 1}: {e}")

    return card_links

def scrape_individual_cards(card_links):
    for index, link in enumerate(card_links):
        try:
            print(f"Scraping card {index + 1} / {len(card_links)}: {link}")
            driver.get(link)
            human_like_delay(2, 4)
            scrape_page()
        except Exception as e:
            print(f"An error occurred while scraping card {index + 1}: {e}")

# Start scraping the main page
try:
    url = 'https://guland.vn/mua-ban-nha-mat-pho-mat-tien-da-nang'  
    card_links = collect_card_links(url)
    scrape_individual_cards(card_links)
except Exception as e:
    print(f"An error occurred while scraping the main page: {e}")
finally:
    df = pd.DataFrame(data_list)
    df.to_csv('scraped_data_only_gianha_GULANG_TESTDRIVERGET.csv',encoding="utf-8", index=False)
    print("Saved successfully")
    driver.quit()

