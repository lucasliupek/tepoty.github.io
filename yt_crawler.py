url = "https://www.youtube.com/user/uzonauzyna"

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


import requests
from multiprocessing.pool import ThreadPool, Pool
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options
import threading
import time

threadLocal = threading.local()
    
def init_driver():
	driver = getattr(threadLocal, 'driver', None)
	if driver is None:
		chromeOptions = webdriver.ChromeOptions()
		chromeOptions.add_argument("--headless")
		driver = webdriver.Chrome("/home/lucasliupek/Desktop/Jive/chromedriver", chrome_options=chromeOptions)
		driver.set_page_load_timeout(15)
		setattr(threadLocal, 'driver', driver)
	return driver


def lookup(driver, url):
    driver.get(url + "/videos?view=0&sort=dd&flow=list&live_view=500")
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    h3s = bs.find_all("h3", {"class": "yt-lockup-title "})

    for h3 in h3s:
        print(h3.get_text() + " https://youtube.com" + h3.find("a", href=True)['href'])


def load_more_content():
    try:
        button = WebDriverWait(driver,10).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "load-more-button")))

        time.sleep(3)
        button.click()

        return True
    except TimeoutException:
        return False

driver = init_driver()
try:
    lookup(driver, url)
finally:
    driver.quit()