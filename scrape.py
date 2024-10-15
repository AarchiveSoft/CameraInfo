"""
TODO: Add special scraping functionality for important brands like Nikon and Sony
The issue is that Video Specs arent found on digicamfinder.com, so i need the info from elsewhere.
"""
import json
import os
import re
import sqlite3
import sys
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
            "rowid"                   : "INTEGER_PRIMARY_KEY",
            "name"                    : "TEXT_NOT_NULL",
            "price"                   : "REAL",
            "body_type"               : "TEXT",
            "weight_inc_batteries"    : "TEXT",
            "dimensions"              : "TEXT",
            "lens_mount"              : "TEXT",
            "display_type"            : "TEXT",
            "burst_fps"               : "TEXT",
            "viewfinder_type"         : "TEXT",
            "maximum_aperture"        : "TEXT",
            "macro_focus_range"       : "TEXT",
            "sensor_size"             : "TEXT",
            "sensor_type"             : "TEXT",
            "image_stabilization"     : "TEXT",
            "max_resolution"          : "TEXT",
            "effective_pixels"        : "REAL",
            "processor"               : "TEXT",
            "number_of_focus_points"  : "INTEGER",
            "iso"                     : "TEXT",
            "boosted_iso_minimum"     : "INTEGER",
            "boosted_iso_maximum"     : "INTEGER",
            "white_balance_presets"   : "INTEGER",
            "custom_white_balance"    : "INTEGER",
            "file_format"             : "TEXT",
            "jpeg_quality_levels"     : "TEXT",
            "image_ratio_wh"          : "TEXT",
            "exposure_modes"          : "TEXT",
            "maximum_shutter_speed"   : "TEXT",
            "minimum_shutter_speed"   : "TEXT",
            "exposure_compensation"   : "TEXT",
            "touch_screen"            : "INTEGER",
            "built_in_flash"          : "INTEGER",
            "gps"                     : "INTEGER",
            "live_view"               : "TEXT",
            "self_timer"              : "TEXT",
            "usb"                     : "TEXT",
            "battery_description"     : "TEXT",
            "battery_life_cipa"       : "INTEGER",
            "viewfinder_coverage"     : "TEXT",
            "viewfinder_magnification": "TEXT",
            "viewfinder_resolution"   : "INTEGER",
            "manual_focus"            : "INTEGER",
            "autofocus"               : "TEXT"
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
        self.conn = sqlite3.connect("CameraSpecs.db")
        self.c = self.conn.cursor()

        self.c.execute("""CREATE TABLE IF NOT EXISTS camera_specs (brand TEXT, name TEXT PRIMARY KEY, announced_date 
        TEXT)""")
        try:
            self.scrape_exec()
        except Exception as e:
            print(f"An Error occured during main execution: {e}")
        finally:
            self.conn.commit()
            self.conn.close()

    def scrape_exec(self):
        """

        Method Name:
            scrape_exec

        Parameters:
            None

        Return Type:
            None

        Description:
            This method prompts the user to choose between scraping and skipping scraping.
            If the user chooses to scrape, it sets up a driver and calls the scrape method.
            If a driver is created, it will sleep for 10 seconds before quitting the driver.
            If no driver is created, it will print a message stating there is no driver to quit
            and close the application.

        """
        print("What do you want to do?"
              "\nEnter '1' to scrape (time consuming)"
              "\nEnter '2' to skip scraping")
        user_input = input("\nAnswer: ")
        while user_input not in ['1', '2']:
            print("\nWrong Input."
                  "\n\nPlease Enter '1' to scrape"
                  "\nOr Enter '2' to skip scraping")
            user_input = input("\nTry again: ")
        user_input = int(user_input)
        if user_input == 1:
            self.driver = self.setup_driver()
            self.scrape_digicamfinder()

        if self.driver:
            time.sleep(10)
            self.driver.quit()
        else:
            print("No Driver to quit, closing application...")

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
            print(f"An error occurred setting up the driver: {e}")

    def wait(self, driver, timeout, condition):
        """

        Initialize the WebDriverWait with a timeout of 10 seconds and wait until the specified condition is met for
        the element located by the given selector using the provided method.

        Parameters:
        - condition: The expected condition to be met for the element
        - by: The mechanism used to find the element (e.g., By.ID, By.CLASS_NAME)
        - selector: The selector used to locate the element (e.g., 'id', 'class')

        """
        return WebDriverWait(driver, timeout).until(condition)

    def scrape_digicamfinder(self):
        """
        Scrapes all links of camera elements from 'https://digicamfinder.com/' website,
        including elements loaded dynamically as you scroll down.

        Parameters:
            - None

        Returns:
            - None
        """
        try:
            # Navigate to the website
            self.driver.get('https://digicamfinder.com/')

            # Optionally close the overlay if present
            try:
                minimize_button = self.wait(
                    self.driver,
                    10,
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-label='Accept overlay.']"))
                )
                minimize_button.click()
                print(f"Clicked minimize button. \n>>Element: {minimize_button}")
            except TimeoutException:
                print("Minimize button not found, continuing...")

            # Wait for the loading spinner to disappear
            self.wait(self.driver, 10, EC.invisibility_of_element_located((By.XPATH, "//span[text()='Loading...']")))

            # determine if link gathering is necessary using txt file
            total_amount_of_cameras_element = self.wait(self.driver, 10, EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".chakra-text.css-cde8r6")))
            total_amount_of_cameras_text = total_amount_of_cameras_element.text
            total_amount_of_cameras = re.sub(r'\D', '', total_amount_of_cameras_text)
            total_amount_of_cameras_int = int(total_amount_of_cameras)

            stored_links = self.count_links()

            print(f"Amount of Links stored is: {stored_links}"
                  f"\nAmount of Cameras on Page: {total_amount_of_cameras_int}")

            if stored_links < total_amount_of_cameras_int:

                # Start scrolling to load more elements
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down the page
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for new elements to load

                    # Wait for the new content to load and check the current scroll height
                    new_height = self.driver.execute_script("return document.body.scrollHeight")

                    # Break if no new content was loaded (end of page)
                    if new_height == last_height:
                        break

                    last_height = new_height

                # Now that all elements are loaded, get the container and scrape the links
                content_container = self.wait(self.driver, 10,
                                              EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-1t2p7x5")))

                camera_elements = content_container.find_elements(By.TAG_NAME, 'a')
                print(f"Total elements found: {len(camera_elements)}")

                # Collect all the links from the 'a' elements
                total_links = 0
                for element in camera_elements:
                    link = element.get_attribute('href')
                    self.links.append(link)
                    total_links += 1
                self.write_links(self.links)
                self.process_cameras_digicamfinder()

            else:
                self.links = self.read_links()
                total_links = self.count_links()
                print(f"{total_amount_of_cameras_int} Cameras are currently listed on the page"
                      f"\n{stored_links} Are already stored from previous Scrape"
                      f"\n\nThe following process is very time-consuming (roughly 45-90 minutes), do you want to "
                      f"proceed, "
                      f"knowing that "
                      f"there's likely NO NEW INFORMATION to be gathered?")
                user_input = input("\n\nType '1' to proceed"
                                   "\nType '2' to abort scraping process"
                                   "\n\nAnswer: ")
                while user_input not in ['1', '2']:
                    user_input = input("\n\nWrong Input!"
                                       "\n\nType '1' to proceed"
                                       "\nType '2' to abort scraping process"
                                       "\n\nAnswer: ")
                if user_input == '2':
                    print("Aborting process...")
                    sys.exit()
                else:
                    print("Proceeding with scraping...")
                    self.process_cameras_digicamfinder()

        except TimeoutException as e:
            print(f"An error occurred during the scraping process: {e}")

        print(f"Total Number of Links gathered: {total_links}")

    def process_cameras_digicamfinder(self):
        """

        Method to process the cameras.

        Parameters:
        - self: the instance of the class
        - links: list of links for the cameras

        Return Type:
        - None

        """
        self.links = self.read_links()
        for link in self.links:
            self.driver.get(link)
            self.wait(self.driver, 10, EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-ha56z6")))
            # get all info for db

            camera_name_element = self.wait(self.driver, 10, EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                               ".chakra-text.css-1myq6hj")))
            camera_name = camera_name_element.text

            brand_name = camera_name.split(' ', 1)[0]

            announced_date_element = self.wait(self.driver, 10, EC.visibility_of_element_located((By.CSS_SELECTOR, ".chakra-text.css-8n0vdq")))
            announced_date_element_text = announced_date_element.text
            announced_date = announced_date_element_text.split(': ')
            announced_date = announced_date[1]

            info_container = self.wait(self.driver, 10,
                                       EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-2tor2e")))

            if info_container is not None:
                divs = info_container.find_elements(By.XPATH, ".//div[not(contains(@class, 'css-wmbgwy'))]")

                div_texts = [div.text for div in divs]

                info_dict = {div_texts[i]: div_texts[i + 1] for i in range(0, len(div_texts), 2)}
            else:
                info_dict = {}
                print("couldn't populate info_dict")

            self.insert_product_specs(brand_name, camera_name, announced_date, info_dict)

    def li_elements(self, element):
        """
        Get all li elements under the given parent element.

        Parameters:
        driver: WebDriver - The driver used to locate the element.
        element: WebElement - The parent element under which to locate li elements.

        Returns:
        list - A list of WebElement objects representing the li elements found.
        """
        all_elements = element.find_elements(By.TAG_NAME, 'li')
        if all_elements is not None:
            return "".join(li.text + "\n" for li in all_elements)
        else:
            return "N/A"

    def bool_elements(self, element):
        """

        Check if the text of a given element is either 'Yes', 'yes', or 'YES'.

        Parameters:
        element: Element to be checked

        Returns:
        True if the text of the element is 'Yes', 'yes', or 'YES', False otherwise

        """
        if element.text in ['Yes', 'yes', 'YES']:
            return True
        elif element.text is None:
            return False
        else:
            return False

    def write_links(self, links):
        """

        Write the given links to a JSON file named "links.json".

        Parameters:
            links (list): A list of links to be written to the JSON file.

        Return type:
            None

        """
        with open("links.json", "w") as file:
            json.dump(links, file)

    def read_links(self):
        """

        Reads and returns a list of links from a JSON file.

        Parameters:
            self

        Returns:
            list: A list of links read from the "links.json" file. If the file is not found, returns an empty list.

        """
        try:
            with open("links.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # return an empty list if file isnt found
        except json.JSONDecodeError:
            return []  # return empty list if theres an issue reading .json (such as an empty file)

    def add_link(self, new_link):
        """

        Add a new link to the existing list of links.

        Parameters:
        new_link (str): The new link to be added.

        Returns:
        None

        """
        links = self.read_links()

        if new_link not in links:
            links.append(new_link)
            self.write_links(links)

    def count_links(self):
        """

        Count the number of links in the provided text data.

        Parameters:
        None

        Returns:
        int: The number of links in the text data.

        """
        links = self.read_links()
        return len(links)

    def add_column_if_not_exists(self, column_name):
        """

        @param column_name: The name of the column to be added to the database table. If the column name contains spaces, parentheses, they will be replaced with underscores and removed, respectively.
        @return: None. If the column does not exist in the table, it will be added as a TEXT type column via ALTER TABLE SQL query.

        """
        column_name = column_name.replace(' ', '_').replace('(', '').replace(')', '')
        self.c.execute("PRAGMA table_info(camera_specs)")
        columns = [info[1] for info in self.c.fetchall()]
        if column_name not in columns:
            self.c.execute(f"ALTER TABLE camera_specs ADD COLUMN {column_name} TEXT")
            self.conn.commit()

    def insert_product_specs(self, brand, name, announced_date, specs):
        """

        Insert product specifications into the database.

        Parameters:
        brand (str): The brand of the product.
        name (str): The name of the product.
        announced_date (str): The date when the product was announced.
        specs (dict): A dictionary containing the product specifications.

        """
        for key in specs.keys():
            self.add_column_if_not_exists(key)

        # prepare dynamic sql query
        columns = ', '.join([key.replace(' ', '_') for key in specs.keys()])
        placeholders = ', '.join(['?' for _ in specs.values()])
        values = list(specs.values())
        self.c.execute(
            f'''INSERT INTO camera_specs (brand, name, announced_date, {columns}) 
                VALUES (?, ?, ?, {placeholders}) 
                ON CONFLICT(name) DO UPDATE SET {", ".join([f"{key.replace(' ', '_')} = ?" for key in specs.keys()])}''',
            [brand] + [name] + [announced_date] + values + values  # Insert values, then provide them again for the
            # update
        )
        self.conn.commit()


if __name__ == '__main__':
    scrape = Scrape()
    scrape.main()
    time.sleep(10)
