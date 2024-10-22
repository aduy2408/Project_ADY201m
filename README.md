## Installation
### Depedencies requirement:
- Selenium
- Geopy
- Mathplotlib 
- Seaborn
- Numpy
- Pandas
- Folium (optional) 
- Python 3.x
### Installing
- After satisfying all the requirement dependencies, you can download the repo:
> to download from master branch
```bash
git clone https://github.com/aduy2408/Project_ADY201m/tree/master
cd Project_ADY201m
```
## How to use (Scraper)
- Run the corresponding scraper, there are 4 scrapers for 4 websites we have made:
    - batdongsan.com.vn
    - alonhadat.com.vn
    - guland.vn
    - nhadatvui.vn 

- For example, when scraping for alonhadat, simply modify the link in the last block of code, in this project, we only aimed for housing in Da Nang, you can change from ``` https://alonhadat.com.vn/can-ban-nha-da-nang-t3/trang-{i}.htm  ```
 it to something like  ``` https://alonhadat.com.vn/can-ban-nha-ho-chi-minh-t2/trang-{i}.htm ``` to scrape housing data from Ho Chi Minh city. The other scrapers should be the same 

- Then you can use the data you scraped youself. 

### Attention
- This project used selenium so speed is out of the question(relatively slow) and sometimes get detected by the website.
- You can use Warp from CloudFlare to bypass some of the websites like ```batdongsan.com.vn```,```guland.vn```, ```nhadatvui.vn```
- As for alonhadat, since the website updated its scraping detection, it relied on identifying images so we could only bypass by hands.