from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the property details page
url = "https://nhadatvui.vn/ban-nha-mat-pho-phuong-binh-thuan-quan-hai-chau/gia-dinh-ban-nha-mat-pho-duong-hoang-dieu-tp-da-nang1710165749"

# Open the webpage
driver.get(url)

# Locate the section containing property details
span_element = driver.find_element(By.CSS_SELECTOR, "i.fa.icon-ndv.iconl-ndv-square.text-lg + span")

# Extract and print the text from the span element
span_text = span_element.text
print(f"Span Text: {span_text}")# Create a dictionary to store the details
details = {}
print(span_text)
# Loop through each detail item and extract text
# for detail in property_details:
#     try:
#         # Get the label and value of each detail
#         label = detail.find_element(By.CLASS_NAME, "real-estate__info-item--name").text.strip()
#         value = detail.find_element(By.CLASS_NAME, "real-estate__info-item--value").text.strip()
#         details[label] = value
#     except:
#         continue

# Close the WebDriver
driver.quit()

# # Print the extracted details
# for key, value in details.items():
#     print(f"{key}: {value}")
