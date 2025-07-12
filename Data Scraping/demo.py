'''
At first i tried to scrape all the info using requests and beautifulsoup for easy understanding and fast progress,
but i was not able to extract it using those API endpoints, because it's not supporting and then i tried to extract using 
graphql end points using payload and all, still it didn't work.

So, the only and final way is to use selenium, where i learned it recently and implemented to get the desired results.
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

# First we need to open the browser and then maximize the window and also initialize webdriverwait()
url = 'https://soilhealth.dac.gov.in/nutrient-dashboard'
driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()
wait = WebDriverWait(driver, 15)
time.sleep(1)

# Click on table view button
tableView_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Table View')]")))
tableView_btn.click()
time.sleep(1)

# Select Micro-nutrients
micro_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Micro-nutrients')]")))
micro_btn.click()
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

'''
Here to extract the data from the table, i firstly tried this using selenium but its not working because,
the page itself is heavily coded with javascript, so while extracting data using it many columns are
missing or not loading, so to avoid that i had to use javascript, where i am not much familiar with that
language, so i took the help from internet and some tools as well.
I was most aware and used requests  and bs4 in the past, where it works on endpoint API's,
and selenium also better for dynamic extraction.

And aslo another problem with this code is, it's not extracting complete columns for macro where it has
18 cols, so i adjusted the scrollLeft element explicitly and finally found a correct value, still its
not collecting village names, then i figured it out that i can use the village names from micro table
where they are same for both tables.
'''
def extract_ag_grid_data_js(driver):
    script = """
        const rows = [];
        const allRows = document.querySelectorAll('.ag-center-cols-container .ag-row');

        allRows.forEach(row => {
            const cells = row.querySelectorAll('.ag-cell');
            const values = [];
            cells.forEach(cell => {
                values.push(cell.innerText.trim());
            });
            rows.push(values);
        });
        return rows;
    """
    return driver.execute_script(script)

def force_horizontal_scroll(driver, scrolls=15):
    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.ag-center-cols-viewport")
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollLeft += 30", scrollable_div)
        time.sleep(0.2)

# extracting micro table
print("Extracting MICRO table")
micro_data = extract_ag_grid_data_js(driver)
village_names = [row[0] for row in micro_data]

# i hardcoded these cols
micro_headers = [
    "Village",
    "Copper_Suf", "Copper_Def",
    "Boron_Suf", "Boron_Def",
    "Sulphur_Suf", "Sulphur_Def",
    "Iron_Suf", "Iron_Def",
    "Zinc_Suf", "Zinc_Def",
    "Manganese_Suf", "Manganese_Def"
]

df_micro = pd.DataFrame(micro_data, columns=micro_headers)
micro_path = os.path.join("data", "raw", "2024-25", "Andhra_Pradesh", "Nellore", "Jaladanki_micro.csv")
os.makedirs(os.path.dirname(micro_path), exist_ok=True)
df_micro.to_csv(micro_path, index=False)
print(f"MICRO saved to path: {micro_path}")

# Switch to macro table now
macro_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Macro-nutrients')]")))
macro_btn.click()
time.sleep(1)

# Scroll to load all columns, we are using this func only for macro because micro loads all cols instantly
force_horizontal_scroll(driver)

# Extract macro table
print("Extracting MACRO table")
macro_data = extract_ag_grid_data_js(driver)

if macro_data:
    print("First Row of Macro Table:", macro_data[0])
    print("Column Count:", len(macro_data[0]))
else:
    print("Macro table is empty.")


# Add village names at the beginning of each row
if len(macro_data) == len(village_names):
    for i in range(len(macro_data)):
        macro_data[i].insert(0, village_names[i])
else:
    print(f"Row mismatch: {len(macro_data)} macro vs {len(village_names)} villages")
    driver.quit()
    exit()

# hardcoded macro table headers
macro_headers = [
    "Village",
    "N_High", "N_Med", "N_Low",
    "P_High", "P_Med", "P_Low",
    "K_High", "K_Med", "K_Low",
    "OC_High", "OC_Med", "OC_Low",
    "EC_NonSaline", "EC_Saline",
    "pH_Alkaline", "pH_Acidic", "pH_Neutral"
]

if all(len(row) == len(macro_headers) for row in macro_data):
    df_macro = pd.DataFrame(macro_data, columns=macro_headers)
    macro_path = os.path.join("data", "raw", "2024-25", "Andhra_Pradesh", "Nellore", "Jaladanki_macro.csv")
    os.makedirs(os.path.dirname(macro_path),exist_ok=True)
    df_macro.to_csv(macro_path, index=False)
    print(f"macro saved to the path: {macro_path}")
else:
    print("Column mismatch!!")


driver.quit()

'''
This is just the demo code for just one micro and macro file.
This is for understanding purpose for the one's who are trying to wokr on this code.
I suggest u to first go with this 'demo.py' file and then process to main file, 
where the code is recursively written to extract the data from alll the states and also it will
be coded in classes and objects methods for better understanding of the errors and logs.
'''