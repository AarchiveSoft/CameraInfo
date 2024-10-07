"""
Temp
"""
import os
import sqlite3
import sys
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Scrape:
    """

    # Method to setup driver for web automation
    #
    # This method sets up the Chrome webdriver for web automation. It first determines the base path where the
    chromedriver
    # executable is located based on whether the script is running as a packaged executable or as a normal
    script. It then
    # creates the chrome options, sets the binary location, and initializes the webdriver service. Finally,
    it creates a
    # new Chrome webdriver instance, configures it with the service and options, and opens a default URL.
    #
    # Parameters:
    #     self: (object) The instance of the class.
    #
    # Returns:
    #     None

    """

    def __init__(self):
        self.table_template = {
            "Price"                : "REAL",
            "Body_Text"            : "TEXT",
            "Body_Type"            : "TEXT",
            "Compact"              : "TEXT",
            "Weight_Inc_Batteries" : "TEXT",
            "Dimensions"           : "TEXT",
            "Viewfinder_Type"      : "TEXT",
            "Optical_Zoom"         : "REAL",
            "Maximum_Aperture"     : "TEXT",
            "Macro_Focus_Range"    : "TEXT",
            "Sensor_Type"          : "TEXT",
            "Image_Stabilization"  : "TEXT",
            "Max_Resolution"       : "TEXT",
            "Effective_Pixels"     : "REAL",
            "ISO"                  : "INTEGER",
            "JPEG_Quality_Levels"  : "TEXT",
            "Image_Ratio_Wh"       : "TEXT",
            "Maximum_Shutter_Speed": "TEXT",
            "Minimum_Shutter Speed": "TEXT",
            "Exposure_Compensation": "TEXT",
            "Touch_Screen"         : "TEXT",
            "Built_In_Flash"       : "TEXT",
            "Live_View"            : "TEXT",
            "Self_Timer"           : "TEXT",
            "Battery_Description"  : "TEXT",
            "Manual_Focus"         : "TEXT",
            "Autofocus"            : "TEXT"
        }

        self.links = []

    def main(self):
        """

        Method name: main

        Description:
        This method is used to perform initial setup by calling setup_driver and setup_db functions.

        Parameters:
        - self: reference to the current instance of the object

        Return Type:
        None

        """
        try:
            driver = self.setup_driver()
            self.scrape(driver)
            self.setup_db()
            time.sleep(10)
            driver.quit()
        except Exception as e:
            print(f"An Error occured: {e}")

    def setup_driver(self):
        """

        # Method to setup driver for web automation
        #
        # This method sets up the Chrome webdriver for web automation. It first determines the base path where the
        chromedriver
        # executable is located based on whether the script is running as a packaged executable or as a normal
        script. It then
        # creates the chrome options, sets the binary location, and initializes the webdriver service. Finally,
        it creates a
        # new Chrome webdriver instance, configures it with the service and options, and opens a default URL.
        #
        # Parameters:
        #     self: (object) The instance of the class.
        #
        # Returns:
        #     None

        """
        if getattr(sys, "frozen", False):
            # Running as packaged executable, driver is in same directory
            base_path = sys._MEIPASS
        else:
            # Running as normal script, driver is in parent directory
            base_path = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.binary_location = os.path.join(base_path, 'chrome', 'win64-118.0.5993.70', 'chrome-win64',
                                                      'chrome.exe')

        service = Service(chromedriver_path)

        try:
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"An error occurred: {e}")

    def setup_db(self):
        """
        Open a connection to a SQLite database called 'CameraSpecs.db'. Create a cursor object for database operations.
        Generate a dynamic SQL query to create a table using the provided table template.
        Execute the SQL command to create the table if it does not already exist and commit the transaction.
        """
        self.conn = sqlite3.connect('CameraSpecs.db')
        self.c = self.conn.cursor()

        # generate SQL Query dynamically
        columns = ',\n'.join([f"{col_name} {col_type}" for col_name, col_type in self.table_template.items()])
        dynamic_sql_command = f"CREATE TABLE IF NOT EXISTS CameraSpecs (\n{columns}\n);"

        self.c.execute(dynamic_sql_command)
        self.conn.commit()

    def wait(self, driver, timeout, condition):
        """

        Initialize the WebDriverWait with a timeout of 10 seconds and wait until the specified condition is met for the element located by the given selector using the provided method.

        Parameters:
        - condition: The expected condition to be met for the element
        - by: The mechanism used to find the element (e.g., By.ID, By.CLASS_NAME)
        - selector: The selector used to locate the element (e.g., 'id', 'class')

        """
        return WebDriverWait(driver, timeout).until(condition)

    def scrape(self, driver):
        """
        Scrapes links of camera elements from 'https://digicamfinder.com/' website.
            - Uses Selenium WebDriver to navigate to the website and locate camera elements.
            - Adds the links of found camera elements to the list 'self.links'.
            - Prints the links.

        If a TimeoutException occurs during the process, it prints an error message.

        Parameters:
            - None

        Returns:
            - None
        """
        try:
            driver.get('https://digicamfinder.com/')

            self.wait(driver, 20, EC.visibility_of_element_located((By.CSS_SELECTOR, "#nav-header")))

            content_container = self.wait(driver, 10,
                                          EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-1t2p7x5")))
            print(f"content_container found. \nElement: {content_container}")

            try:
                elements = self.wait(driver, 10, EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))
                print(f"elements found: {elements}")
            except TimeoutException as e:
                print(f"failed to locate the tagnamed 'a's in the content_container: {e}")

            camera_elements = driver.find_elements(By.CSS_SELECTOR, ".css-1t2p7x5 a")
            print(f"camera_elements found: {camera_elements}")

            for element in camera_elements:
                link = element.get_attribute('href')
                self.links.append(link)

        except TimeoutException as e:
            print(f"An Error occured during the scraping process: {e}")

        for link in self.links:
            print(link)


if __name__ == '__main__':
    scrape = Scrape()
    scrape.main()
    time.sleep(10)
