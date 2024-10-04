"""
Temp
"""
import os
import sqlite3
import sys

from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.service import Service


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
            "Body"                 : "TEXT",
            "Body Type"            : "TEXT",
            "Compact"              : "TEXT",
            "Weight Inc Batteries" : "TEXT",
            "Dimensions"           : "TEXT",
            "Viewfinder Type"      : "TEXT",
            "Optical Zoom"         : "REAL",
            "Maximum Aperture"     : "TEXT",
            "Macro Focus Range"    : "TEXT",
            "Sensor Type"          : "TEXT",
            "Image Stabilization"  : "TEXT",
            "Max Resolution"       : "TEXT",
            "Effective Pixels"     : "REAL",
            "ISO"                  : "INTEGER",
            "JPEG Quality Levels"  : "TEXT",
            "Image Ratio Wh"       : "TEXT",
            "Maximum Shutter Speed": "TEXT",
            "Minimum Shutter Speed": "TEXT",
            "Exposure Compensation": "TEXT",
            "Touch Screen"         : "TEXT",
            "Built In Flash"       : "TEXT",
            "Live View"            : "TEXT",
            "Self Timer"           : "TEXT",
            "Battery Description"  : "TEXT",
            "Manual Focus"         : "TEXT",
            "Autofocus"            : "TEXT"
        }

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
        self.setup_driver()
        self.setup_db()

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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.path.join(base_path, 'chrome', 'win64-118.0.5993.70', 'chrome-win64',
                                                      'chrome.exe')

        service = Service(chromedriver_path)

        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.get('https://digicamfinder.com/')
        except Exception as e:
            print(f"An error occurred: {e}")

    def setup_db(self):
        self.conn = sqlite3.connect('CameraSpecs.db')
        self.c = self.conn.cursor()

        # generate SQL Query dynamically
        columns = ',\n'.join([f"{col_name} {col_type}" for col_name, col_type in self.table_template.items()])
        dynamic_sql_command = f"CREATE TABLE IF NOT EXISTS CameraSpecs (\n{columns}\n);"

        self.c.execute(dynamic_sql_command)
        self.conn.commit()


if __name__ == '__main__':
    scrape = Scrape()
    scrape.main()
