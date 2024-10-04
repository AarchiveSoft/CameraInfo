"""
Temp
"""
import os
import sys

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import chrome
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Scrape:

    if getattr(sys, "frozen", False):
        # Running as packaged executable, driver is in same directory
        base_path = sys._MEIPASS
    else:
        # Running as normal script, driver is in parent directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.path.join(base_path, 'chrome', 'win64-118.0.5993.70', 'chrome-win64',
                                                  'chrome.exe')

    service = Service(chromedriver_path)

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"An error occurred: {e}")

    