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
STANDARD_KEYS = ['Diện tích', 'Chiều rộng','Chiều dài','Năm xây dựng', 'Giấy tờ pháp lý','Hiện trạng nhà'
                 'Phòng ngủ','Phòng tắm', 'Vị trí', 'Trạng thái sử dụng', 'Số tầng', 'Đường rộng','Hướng','Kết cấu']
def remove_header():
    """Remove the header with class 'sdb-hdr-n' from the page."""
    try:
        driver.execute_script("""
            var header = document.querySelector('.px-4');
            if (header) {
                header.remove();
            }
        """)
        print("Header element removed.")
    except Exception as e:
        print(f"Failed to remove header element: {e}")
def remove_search_form():
    script = """
    var element = document.querySelector('.px-8');
    if (element) {
        element.remove();
    }
    """
    driver.execute_script(script)
    print("Search form removed.")
# Human-like delay function
def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    human_like_delay(1, 3)

def scrape_page():
    data = {}
    try:
        price = driver.find_element(By.CLASS_NAME, 'price').text.strip()
        data['price'] = price
        
        
        # Extract detailed property information
        try:
            # Locate the details section by its unique ID 'content-tab-info'
            details_section = driver.find_element(By.ID, 'content-tab-info')
            detail_items = details_section.find_elements(By.TAG_NAME, 'li')
            
            for item in detail_items:
                try:
                    # Get the key (label) and value spans within each list item
                    key_span = item.find_element(By.XPATH, './/span[2]')
                    value_span = item.find_element(By.XPATH, './/span[2]/following-sibling::span')
                    key = key_span.text.strip()
                    value = value_span.text.strip()
                    data[key] = value
                except NoSuchElementException:
                    continue

        except NoSuchElementException:
            print("Detail section not found.")
        
        # Ensure all standard keys are filled
        for key in STANDARD_KEYS:
            if key not in data:
                data[key] = None

        print(f"Collected data: {data}")
        data_list.append(data)
    except TimeoutException:
        print("Timeout reached while trying to load the card page.")
    except Exception as e:
        print(f"An error occurred while extracting data: {e}")
def scrape_main_page(url):
    driver.get(url)
    scroll_to_bottom()
    human_like_delay(2, 4)

    try:
        # Wait for the main container of cards to be present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.box-item.box-item-hover.border.rounded.bg-white')))
    except TimeoutException:
        print(f"Timeout: Main page elements not loaded at {url}.")
        return []

    remove_header()
    remove_search_form()

    # Get all card elements
    cards = driver.find_elements(By.CSS_SELECTOR, '.box-item.box-item-hover.border.rounded.bg-white')
    card_links = []

    for index, card in enumerate(cards):
        try:
            # Scroll into view to make sure the element is visible and interactive
            driver.execute_script("arguments[0].scrollIntoView(true);", card)
            human_like_delay(1, 2)

            # Find the nested <a> tag within the card and get the href attribute
            link_element = card.find_element(By.CSS_SELECTOR, 'a.p-2.pb-3.grid')
            link = link_element.get_attribute('href')
            
            if link:
                card_links.append(link)
                print(f"Collected link for card {index + 1}: {link}")
            else:
                print(f"No href found for card {index + 1}.")
        except NoSuchElementException:
            print(f"Link not found for card {index + 1}.")
        except TimeoutException:
            print(f"Timeout: Link not found for card {index + 1}.")
        except StaleElementReferenceException:
            print(f"Stale reference for card {index + 1}. Re-fetching elements.")
            return []  # To force re-fetching elements
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
    for i in range(1,182):
        try:

            url = f'https://nhadatvui.vn/mua-ban-nha-rieng-tp-da-nang?ctIds=14%2C25%2C6&page={i}'
            card_links = scrape_main_page(url)_
            scrape_individual_cards(card_links)
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
