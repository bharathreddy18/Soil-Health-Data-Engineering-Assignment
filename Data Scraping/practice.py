import os
import shutil
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DOWNLOAD_TEMP = os.path.abspath("downloads_temp")
DATA_DIR = os.path.abspath("data/raw")
BASE_URL = "https://soilhealth.dac.gov.in/nutrient-dashboard"
CYCLES = ["2023-24", "2024-25"]

class SoilHealthScraper:
    def __init__(self, download_dir):
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def click_dropdown_option(self, drop_id, option_text):
        try:
            self.wait.until(EC.element_to_be_clickable((By.ID, drop_id))).click()
            time.sleep(0.5)
            options_xpath = "//ul[@role='listbox']//li"
            options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, options_xpath)))

            for item in options:
                if item.text.strip().upper() == option_text.strip().upper():
                    # driver.execute_script("arguments[0].scrollIntoView(true);", item)
                    # time.sleep(0.2)
                    item.click()
                    time.sleep(0.5)
                    break

            # Close dropdown overlay
            # self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            # time.sleep(0.5)
            # WebDriverWait(self.driver, 5).until_not(
            #     EC.presence_of_element_located((By.XPATH, "//ul[@role='listbox']"))
            # )

        except Exception as e:
            logging.error(f"Dropdown click failed for {drop_id} -> {option_text}: {e}")
            raise

    def download_csv(self, cycle, state, district, block):
        try:
            logging.info(f"Scraping: {cycle} > {state} > {district} > {block}")
            block_dir = os.path.join(DATA_DIR, cycle, state, district)
            cleaned_block = block.split('-')[0].strip()
            macro_path = os.path.join(block_dir, f'{cleaned_block}_macro.csv')
            micro_path = os.path.join(block_dir, f'{cleaned_block}_micro.csv')
            logging.info(f'Downloading Macro for {cleaned_block}.....')

            # Open Filter
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))).click()
            time.sleep(0.5)

            # Select block
            self.click_dropdown_option("Block", block)
            time.sleep(0.5)

            # Close Filter
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))).click()
            time.sleep(0.5)

            # clicking the Macro nutrition tab
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//button[contains(text(), 'Macro-nutrients')]")))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Macro-nutrients')]"))).click()
            time.sleep(0.5)

            # Check if Export button is disabled or enabled
            export_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
            is_disabled = "Mui-disabled" in export_btn.get_attribute("class") or export_btn.get_attribute("disabled")

            if is_disabled:
                logging.warning(f"SKipping (No Data): {cycle} | {state} | {district} | {block}")
                return
            
            # Click Export > CSV
            export_btn.click()
            time.sleep(0.5)

            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'CSV')]"))).click()
            time.sleep(1)
            
            ActionChains(self.driver).move_by_offset(5, 5).click().perform() # or below we can use
            # driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)

            timeout = 15
            start = time.time()
            downloaded = None
            while time.time() - start < timeout:
                files = [os.path.join(DOWNLOAD_TEMP, f) for f in os.listdir(DOWNLOAD_TEMP) if f.endswith('.csv')]
                if files:
                    downloaded = max(files, key=os.path.getctime)
                    break
                time.sleep(0.5)
            if not downloaded:
                logging.error(f"Download failed for {cleaned_block} Macro File")
            
            os.makedirs(os.path.dirname(macro_path), exist_ok=True)
            shutil.move(downloaded, macro_path)
            logging.info(f"Saved Macro CSV to {macro_path}")

            # clicking the Micro nutrition tab
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//button[contains(text(), 'Micro-nutrients')]")))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Micro-nutrients')]"))).click()
            time.sleep(0.5)

            # Check if Export button is disabled or enabled
            export_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
            is_disabled = "Mui-disabled" in export_btn.get_attribute("class") or export_btn.get_attribute("disabled")

            if is_disabled:
                logging.warning(f"SKipping (No Data): {cycle} | {state} | {district} | {block}")
                return
            
            # Click Export > CSV
            export_btn.click()
            time.sleep(0.5)

            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'CSV')]"))).click()
            time.sleep(1)
            
            ActionChains(self.driver).move_by_offset(5, 5).click().perform() # or below we can use
            # driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)

            timeout = 15
            start = time.time()
            downloaded = None
            while time.time() - start < timeout:
                files = [os.path.join(DOWNLOAD_TEMP, f) for f in os.listdir(DOWNLOAD_TEMP) if f.endswith('.csv')]
                if files:
                    downloaded = max(files, key=os.path.getctime)
                    break
                time.sleep(0.5)
            if not downloaded:
                logging.error(f"Download failed for {cleaned_block} Micro File")
            
            os.makedirs(os.path.dirname(micro_path), exist_ok=True)
            shutil.move(downloaded, micro_path)
            logging.info(f"Saved Micro CSV to {micro_path}")
        
        except Exception as e:
            print(f"Error occured for block: {e}")

    # def scrape_block(self, cycle, state, district, block):
    #     logging.info(f"Scraping: {cycle} > {state} > {district} > {block}")
    #     block_dir = os.path.join(DATA_DIR, cycle, state, district)
    #     cleaned_block = block.split('-')[0].strip()
    #     macro_path = os.path.join(block_dir, f"{cleaned_block}_macro.csv")
    #     micro_path = os.path.join(block_dir, f"{cleaned_block}_micro.csv")
    #     logging.info(f"Attempting Macro download for {cleaned_block}...")
    #     macro_success = self.download_csv(cycle, state, district, block, "Macro-nutrients", macro_path)
    #     logging.info(f"Macro result: {macro_success}")
    #     logging.info(f"Attempting Micro download for {cleaned_block}...")
    #     micro_success = self.download_csv(cycle, state, district, block, "Micro-nutrients", micro_path)
    #     logging.info(f"Micro result: {micro_success}")

    def main(self):
        os.makedirs(DOWNLOAD_TEMP, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)

        self.driver.get(BASE_URL)
        self.driver.maximize_window()
        time.sleep(1)

        logging.info("Clicking Table View button")
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Table View')]"))).click()
        time.sleep(1)

        for cycle in CYCLES:
            logging.info(f"Selecting cycle: {cycle}")
            self.click_dropdown_option("Cycle", cycle)
            time.sleep(0.5)

            # Open Filter
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))).click()
            time.sleep(0.5)

            # Select state
            self.wait.until(EC.element_to_be_clickable((By.ID, "State"))).click()
            time.sleep(0.5)

            states = [el.text.strip() for el in self.driver.find_elements(By.XPATH, "//ul[@role='listbox']//li") if el.text.strip()]
            logging.info(f"Found states: {states}")

            # Select state again to avoid overlay issues
            self.wait.until(EC.element_to_be_clickable((By.ID, "State"))).click()
            time.sleep(0.5)

            # Now finally close the filter
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))).click()
            time.sleep(1)

            for state in states:
                try:
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))).click()
                    time.sleep(0.5)

                    self.click_dropdown_option("State", state)
                    time.sleep(0.5)

                    # Select District
                    self.wait.until(EC.element_to_be_clickable((By.ID, 'District'))).click()
                    time.sleep(0.5)

                    districts = [el.text.strip() for el in self.driver.find_elements(By.XPATH, "//ul[@role='listbox']//li") if el.text.strip()]
                    logging.info(f"For State: {state}\nFound Districts: {districts}")

                    self.wait.until(EC.element_to_be_clickable((By.ID, 'District'))).click()
                    time.sleep(0.5)

                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))).click()
                    time.sleep(1)

                    for district in districts:
                        try:
                            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))).click()
                            time.sleep(0.5)

                            self.click_dropdown_option("District", district)
                            time.sleep(0.5)

                            # Select Block
                            self.wait.until(EC.element_to_be_clickable((By.ID, 'Block'))).click()
                            time.sleep(0.5)

                            blocks = [el.text.strip() for el in self.driver.find_elements(By.XPATH, "//ul[@role='listbox']//li") if el.text.strip()]
                            logging.info(f"For State: {state} and district: {district}\nFound Blocks: {blocks}")

                            self.wait.until(EC.element_to_be_clickable((By.ID, 'Block'))).click()
                            time.sleep(0.5)

                            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))).click()
                            time.sleep(1)

                            for block in blocks:
                                self.download_csv(cycle, state, district, block)
                        except Exception as e:
                            logging.error(f"Failed district: {district} | {e}")
                except Exception as e:
                    logging.error(f"Failed State: {state} | {e}")

        self.driver.quit()
        try:
            shutil.rmtree(DOWNLOAD_TEMP)
        except Exception:
            pass

if __name__ == "__main__":
    scraper = SoilHealthScraper(download_dir=DOWNLOAD_TEMP)
    scraper.main()