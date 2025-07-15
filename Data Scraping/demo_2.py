from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

# First we need to open the browser and then maximize the window and also initialize webdriverwait()
DOWNLOAD_TEMP = os.path.abspath("downloads_temp")
DATA_DIR = os.path.abspath("data/raw")
url = 'https://soilhealth.dac.gov.in/nutrient-dashboard'

options = webdriver.ChromeOptions()
prefs = {
        "download.default_directory": DOWNLOAD_TEMP,
        "download.prompt_for_download": True,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }

options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
driver.maximize_window()
driver.get(url)
# Click on table view button
tableView_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Table View')]")))
tableView_btn.click()
time.sleep(1)

# Select Cycle
drop_cycle = wait.until(EC.element_to_be_clickable((By.ID, 'Cycle')))
drop_cycle.click()
time.sleep(1)
cycle_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), '2024-25')]")))
cycle_option.click()
time.sleep(1)

# Click Filter button
filter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]")))
filter_btn.click()
time.sleep(1)

# first we select State
drop_state = wait.until(EC.element_to_be_clickable((By.ID, 'State')))
drop_state.click()
time.sleep(1)
state_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'ANDHRA PRADESH')]")))
state_option.click()
time.sleep(1)

# Select District
drop_district = wait.until(EC.element_to_be_clickable((By.ID, 'District')))
drop_district.click()
time.sleep(1)
district_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'SPSR NELLORE')]")))
district_option.click()
time.sleep(1)

# Select Block
drop_block = wait.until(EC.element_to_be_clickable((By.ID, 'Block')))
drop_block.click()
time.sleep(1)
block_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'JALADANKI - 5388')]")))
block_option.click()
time.sleep(1)

# Close button
close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]")))
close_btn.click()
time.sleep(5)

# Select Micro-nutrients
micro_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Micro-nutrients')]")))
micro_btn.click()
time.sleep(1)

wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Export')]"))).click()
time.sleep(1)

wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'CSV')]"))).click()
time.sleep(10)