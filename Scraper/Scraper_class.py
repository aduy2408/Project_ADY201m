from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time
import random
import re
### Note: Tai library selenium truoc bang terminal cua vscode(K lam dc thi len youtube tim): python -m pip install selenium
### Sau do len chromedriver tim phien ban: https://sites.google.com/chromium.org/driver/downloads?authuser=0
### Tai lai chrome phien ban giong voi version cua chromedriver da tai(xoa chrome phien ban hien tai neu co, dong thoi block updates cua chrome)
### Them duong dan toi chromedriver vao PATH de selenium biet, neu khong phai tu specify path toi chromedriver trong code
### Vay la xong ve phan set up, chi viec run code, sua so luong o vong for de biet scrape trang nao den trang nao
### Rieng voi nha mang binh thuong thi co kha nang vao web lag / bi chan ip sau vai lan connect vao web batdongsan, trong truong hop do
### thi xem xet su dung WARP cua cloudflare thi no se cho bypass cai verify human

class RealEstateScraper:
    def __init__(self):
        # Setup ChromeDriver options
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
        })
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.data_list = []
        self.STANDARD_KEYS = ['Diện tích', 'Mức giá', 'Mặt tiền', 'Đường vào', 'Hướng nhà', 
                              'Hướng ban công', 'Số phòng ngủ', 'Số toilet', 'Pháp lý', 
                              'Số tầng', 'Nội thất', 'Longitude', 'Latitude']
    #Xoa quang cao
    def remove_unwanted_div(self):
        script = """
        var element = document.querySelector('.re__listing-verified-similar-v2.js__listing-verified-similar');
        if (element) {
            element.remove();
        }
        """
        self.driver.execute_script(script)
        print("Ad removed.")
    #Xoa thanh tim kiem de tranh anh huong luc click
    def remove_search_form(self):
        script = """
        var element = document.querySelector('#boxSearchForm');
        if (element) {
            element.remove();
        }
        """
        self.driver.execute_script(script)
        print("Search form removed.")
    #Delay
    def human_like_delay(self, min_time=1, max_time=3):
        time.sleep(random.uniform(min_time, max_time))
    #Dong pop up
    def close_popup(self):
        try:
            popup_close_button = self.driver.find_element(By.CSS_SELECTOR, '.nomodal')
            self.driver.execute_script("""
                var element = document.querySelector('.nomodal');
                if (element) {
                    element.remove();
                }
            """)
            print("Popup closed.")
        except NoSuchElementException:
            print("No popup found.")
    #Lay toa do
    def extract_latitude_longitude(self):
        try:
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[data-src]')))
            data_src = iframe.get_attribute('data-src')

            
            pattern = r"q=([\d.]+),([\d.]+)&"
            match = re.search(pattern, data_src)
            
            if match:
                latitude = match.group(1)
                longitude = match.group(2)
                return latitude, longitude
            else:
                print("Latitude and Longitude not found in the URL.")
                return None, None
        except Exception as e:
            print(f"Error extracting latitude and longitude: {e}")
            return None, None
    #Luot xuong duoi lan dau tien de tranh phat hien bot
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.human_like_delay(1, 3)
    #Main function de scrape
    def scrape_page(self):
        data = {}
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 're__pr-specs-content-item-value')))
            
            specs_items = self.driver.find_elements(By.CSS_SELECTOR, '.re__pr-specs-content-item')
            for item in specs_items:
                title_element = item.find_element(By.CLASS_NAME, 're__pr-specs-content-item-title')
                value_element = item.find_element(By.CLASS_NAME, 're__pr-specs-content-item-value')

                title = title_element.text.strip()
                value = value_element.text.strip()

                data[title] = value

            latitude, longitude = self.extract_latitude_longitude()
            if latitude and longitude:
                data['Latitude'] = latitude
                data['Longitude'] = longitude

            for key in self.STANDARD_KEYS:
                if key not in data:
                    data[key] = None

            print(data)
            self.data_list.append(data)
        except TimeoutException:
            print("Timeout reached while trying to load the card page.")
    #Scrape page chinh de lay url
    def scrape_main_page(self, url):
        self.driver.get(url)
        self.scroll_to_bottom()
        self.human_like_delay(2, 4)
        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'js__product-link-for-product-id')))
        self.remove_unwanted_div()

        cards = self.driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')

        for i in range(len(cards) - 1):
            try:
                print(len(cards))
                print(f"Clicking on card {i + 1}...")
                self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'js__product-link-for-product-id')))
                self.remove_unwanted_div()
                self.close_popup()
                cards = self.driver.find_elements(By.CLASS_NAME, 'js__product-link-for-product-id')
                self.remove_search_form()
                self.human_like_delay(1, 3)

                self.driver.execute_script("arguments[0].scrollIntoView();", cards[i])
                self.human_like_delay(1, 2)
                cards[i].click()

                self.human_like_delay(1, 3)

                self.scrape_page()

                self.human_like_delay(2, 4)
            except Exception as e:
                print(f"An error occurred while clicking on card {i + 1}: {e}")
            finally:
                try:
                    self.driver.back()
                except:
                    pass
    #luu csv
    def save_to_csv(self, filename):
        df = pd.DataFrame(self.data_list)
        df.to_csv(filename, encoding="utf-8", index=False)
        print(f"Data saved to {filename}")
    #Loop de lay het cac trang co url
    def scrape_pages(self, start_page, end_page, base_url, filename):
        try:
            for i in range(start_page, end_page):
                try:
                    url = f'{base_url}/p{i}'
                    self.scrape_main_page(url)
                except Exception as e:
                    print(f"Error while scraping page {i}: {e}")
                    continue
        except Exception as e:
            print(f"An error occurred during the scraping process: {e}")
        finally:
            self.save_to_csv(filename)  # Save the CSV file even if there's an error or browser crash.
            if self.driver:
                self.close()

    def close(self):
        self.driver.quit()



if __name__ == "__main__":
    scraper = RealEstateScraper()
    scraper.scrape_pages(start_page=101, end_page=200, base_url='https://batdongsan.com.vn/nha-dat-ban-da-nang', filename='scraped_data_NEW_bds.csv')
    scraper.close()