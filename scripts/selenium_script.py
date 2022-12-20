import requests
import colorama
import lxml
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from tqdm import tqdm

TOTAL_NUMBER_OF_NEWS = 10000
FOR_URL = 'https://www.volgograd.kp.ru'
NAME_FILE_WITH_LINKS = "news_link.txt"


options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
browser = Chrome(service=Service('C:\chromedriver\chromedriver.exe'), options=options)
url = 'https://www.volgograd.kp.ru/online/'

# browser.get(url)
# button = browser.find_element_by_css_selector("#app > div.sc-13iz5ku-0.lnKmOk > div > div.sc-1izj9yl-0.mgzJs > div > div:nth-child(2) > div.sc-1ktpw9t-0.cwduiG > div > button")
# # news = browser.find_elements_by_class_name("sc-1tputnk-13")
# # print(len(news))

# # headers = requests.utils.default_headers()
# # domain_name = urlparse(url).netloc
# soup = BeautifulSoup(browser.page_source, "lxml")

# events = soup.find_all('div', class_="sc-1tputnk-13")

browser.get(url)
button = browser.find_element_by_css_selector("#app > div.sc-13iz5ku-0.lnKmOk > div > div.sc-1izj9yl-0.mgzJs > div > div:nth-child(2) > div.sc-1ktpw9t-0.cwduiG > div > button")
soup = BeautifulSoup(browser.page_source, "lxml")

counter = 0
last_href: str = ''
news_links: list = []
flag = False
browser.get(url)
while counter < 10000:
   
    soup = BeautifulSoup(browser.page_source, "lxml")
    
    if counter == 0:
        all_pages = soup.find_all('div', class_="sc-1ktpw9t-1")
    else:
        all_pages = soup.find_all('div', class_="sc-1ktpw9t-0")
    pages = all_pages[-1]
    for page in pages:
        events = page.find_all('div', class_="sc-1tputnk-13")
        for event in events:
            news_link = event.find('a', class_='sc-1tputnk-2').get('href')
            full_news_link = FOR_URL + news_link
            news_links.append(full_news_link)
            counter += 1
            # print(news_link)
    last_href = news_links[-1]
    flag = False
    button = browser.find_element_by_css_selector("#app > div.sc-13iz5ku-0.lnKmOk > div > div.sc-1izj9yl-0.mgzJs > div > div:nth-child(2) > div.sc-1ktpw9t-0.cwduiG > div > button")
    button.click()
    sleep(2.8)
    # counter += len(news_links)
    print(counter)
    
with open(NAME_FILE_WITH_LINKS, "w") as file:
    for link in news_links:
        file.write(link + '\n')