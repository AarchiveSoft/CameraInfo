"""
Temp
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
        try:
            self.setup_db()
        except Exception as e:
            print(f"An Error occured setting up the db: {e}")
        try:
            self.scrape_exec()
        except Exception as e:
            print(f"An Error occured during main execution: {e}")

    # TODO Rename this here and in `main`
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
            self.scrape(self.driver)

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

        Initialize the WebDriverWait with a timeout of 10 seconds and wait until the specified condition is met for
        the element located by the given selector using the provided method.

        Parameters:
        - condition: The expected condition to be met for the element
        - by: The mechanism used to find the element (e.g., By.ID, By.CLASS_NAME)
        - selector: The selector used to locate the element (e.g., 'id', 'class')

        """
        return WebDriverWait(driver, timeout).until(condition)

    def scrape(self, driver):
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
                self.process_cameras()

            else:
                self.links = self.read_links()
                total_links = self.count_links()
                print(f"{total_amount_of_cameras_int} Cameras are currently listed on the page"
                      f"\n{stored_links} Are already stored from previous Scrape"
                      f"\n\nThe following process is very time-consuming, do you want to proceed, knowing that "
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
                    self.process_cameras()

        except TimeoutException as e:
            print(f"An error occurred during the scraping process: {e}")

        # Print all collected links
        # for link in self.links:
        # print(link)
        print(f"Total Number of Links gathered: {total_links}")

    def process_cameras(self):
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

            info_container = self.wait(self.driver, 10,
                                       EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-2tor2e")))

            if info_container is not None:
                info_divs = info_container.find_elements(By.TAG_NAME, "div")
                info_elements = {
                    "price"                           : str(info_divs[2].text),
                    "body_type"                       : info_divs[5].text,
                    "weight_inc_batteries"            : info_divs[7].text,
                    "dimensions"                      : info_divs[9].text,
                    "lens_mount"                      : info_divs[11].text,
                    "display_type"                    : info_divs[13].text,
                    "burst_fps"                       : info_divs[15].text,
                    "viewfinder_type"                 : info_divs[17].text,
                    "sensor_size"                     : info_divs[21].text,
                    "sensor_type"                     : info_divs[23].text,
                    "image_stabilization"             : info_divs[25].text,
                    "max_resolution"                  : info_divs[27].text,
                    "effective_pixels"                : info_divs[29].text,
                    "processor"                       : info_divs[30].text,
                    "number_of_focus_points"          : str(info_divs[32].text),
                    "iso"                             : info_divs[35].text,
                    "boosted_iso_minimum"             : str(info_divs[37].text),
                    "boosted_iso_maximum"             : str(info_divs[39].text),
                    "white_balance_presets"           : str(info_divs[41].text),
                    "custom_white_balance"            : info_divs[43].text,
                    "file_format"                     : self.li_elements(info_divs[45]),
                    "jpeg_quality_levels"             : info_divs[47].text,
                    "image_ratio_wh"                  : info_divs[49].text,
                    "exposure_modes"                  : self.li_elements(info_divs[51]),
                    "maximum_shutter_speed"           : info_divs[54].text,
                    "maximum_shutter_speed_electronic": info_divs[56].text,
                    "minimum_shutter_speed"           : info_divs[58].text,
                    "exposure_compensation"           : info_divs[60].text,
                    "touch_screen"                    : self.bool_elements(info_divs[62]),  # this
                    "built_in_flash"                  : self.bool_elements(info_divs[64]),  # this
                    "gps"                             : self.bool_elements(info_divs[66]),  # this
                    "live_view"                       : self.bool_elements(info_divs[68]),  # this
                    "self_timer"                      : self.bool_elements(info_divs[70]),  # and this all BOOL,
                    "usb"                             : info_divs[72].text,
                    "battery_description"             : info_divs[74].text,
                    "battery_life_cipa"               : info_divs[76].text,
                    "viewfinder_coverage"             : info_divs[78].text,
                    "viewfinder_magnification"        : info_divs[80].text,
                    "viewfinder_resolution"           : info_divs[82].text,
                    "manual_focus"                    : self.bool_elements(info_divs[84]),  # TODO: bool, handle later
                    "autofocus"                       : self.li_elements(info_divs[86])
                }
            else:
                print("couldn't find info container")

            dynamic_sql_command_start = "INSERT INTO CameraSpecs (name, "
            columns = ', '.join([f"{key}" for key, value in info_elements.items()])
            dynamic_sql_command_mid = ")\nVALUES (?, "
            question_marks = ', '.join(["?" for key, value in info_elements.items()])
            dynamic_sql_command_mid2 = ")"

            dynamic_sql_command = (dynamic_sql_command_start + columns + dynamic_sql_command_mid + question_marks +
                                   dynamic_sql_command_mid2)

            dynamic_variable_insert = [value for key, value in info_elements.items()]
            dynamic_variable_insert = (camera_name,) + tuple(dynamic_variable_insert)

            self.c.execute(dynamic_sql_command, tuple(dynamic_variable_insert))
            self.conn.commit()

            """         
            for column, value in info_elements:
    
            price = 0.0
            name = ""
            body_type = ""
            weight_inc_batteries = ""
            dimensions = ""
            lens_mount = ""
            display_type = ""
            burst_fps = ""
            viewfinder_type = ""
            optical_zoom = 0.0
            maximum_aperture = ""
            macro_focus_range = ""
            sensor_size = ""
            sensor_type = ""
            image_stabilization = ""
            max_resolution = ""
            effective_pixels = ""
            processor = ""
            number_of_focus_points = 0
            iso = ""
            boosted_iso_minimum = 0
            boosted_iso_maximum = 0
            white_balance_presets = 0
            custom_white_balance = 0
            file_format = ""
            jpeg_quality_levels = ""
            image_ratio_wh = ""
            exposure_modes = ""
            maximum_shutter_speed = ""
            minimum_shutter_speed = ""
            exposure_compensation = ""
            touch_screen = 0
            built_in_flash = 0
            gps = 0
            live_view = ""
            self_timer = ""
            usb = ""
            battery_description = ""
            battery_life_cipa = 0
            viewfinder_coverage = ""
            viewfinder_magnification = ""
            viewfinder_resolution = 0
            manual_focus = 0
            autofocus = ""
            """

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


if __name__ == '__main__':
    scrape = Scrape()
    scrape.main()
    time.sleep(10)
