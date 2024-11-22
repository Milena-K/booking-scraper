from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import json
import pandas as pd
import os

from helpers import get_cards

# Directory path
directory = "data"

# Check if directory exists, if not, create it
if not os.path.exists(directory):
    os.mkdir(directory)

# Set Chrome options to ignore SSL errors
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--allow-insecure-localhost")
# chrome_options.add_argument("--headless")

# Initialize ChromeDriver with these options
driver = webdriver.Chrome(options=chrome_options)

# take settings from json
with open("config.json", "r") as file:
    config = json.load(file)

# take places from file
with open("locations.txt", "r") as file:
    places = [line.strip().lower() for line in file]

# store the location data here
entries = {}

for place in places:
    entries[place] = []

# open page
driver.get("https://www.booking.com/")

print("Booking.com is open")
for place in places:
    print()
    print("=======================================")
    print(f"Searching locations for {place}...")
    print("=======================================")
    time.sleep(config["delay"])

    # disable ad
    try:
        cancel_ad = driver.find_element(By.XPATH, '//*[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 f4552b6561"]').click()
    except:
        pass
        # print("The first popup ad didn't show up")

    # enter the name of the place
    input_place = driver.find_element(By.XPATH, f"//input[@placeholder='Where are you going?']")
    time.sleep(config["delay"])
    # Create an ActionChain instance
    actions = ActionChains(driver)
    # Perform a triple-click
    actions.click(input_place).click(input_place).click(input_place).perform()
    # Type a backspace
    actions.send_keys(Keys.BACKSPACE).perform()
    input_place.send_keys(place)

    # calculate dates
    current_date = datetime.now().date()
    start_date = datetime.now().date() + timedelta(config["check_in_days_ahead"])
    end_date = start_date + timedelta(config["stay_duration"])
    time.sleep(config["delay"])

    # enter dates
    date_element = driver.find_element(By.XPATH, '//*[@data-testid="date-display-field-start"]').click()
    time.sleep(config["delay"])

    start_day = driver.find_element(By.XPATH, f"//*[@aria-label=\"{start_date.strftime('%d %B %Y')}\"]")
    ActionChains(driver).move_to_element(start_day).click().perform()
    time.sleep(config["delay"])

    end_day = driver.find_element(By.XPATH, f"//*[@aria-label=\"{end_date.strftime('%d %B %Y')}\"]")
    ActionChains(driver).move_to_element(end_day).click().perform()
    time.sleep(config["delay"])

    # click ze button
    search_btn = driver.find_element(By.XPATH, '//*[@class="a83ed08757 c21c56c305 a4c1805887 f671049264 a2abacf76b c082d89982 cceeb8986b b9fd3c6b3c"]').click()
    time.sleep(config["delay"])
    ###### STEP 2: collect ze data ############


    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 200);")
    time.sleep(config["delay"])
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 200);")
    time.sleep(config["delay"])
    # = 75 entry

    try:
        load_more_btn = WebDriverWait(driver, 5000).until(
            EC.presence_of_element_located((By.XPATH, "//button[span[text()='Load more results']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_btn)
        time.sleep(config["delay"])
        load_more_btn.click()
    except:
        pass
        # print("First load more button did not appear within the timeout.")

    # cancel the second ad
    try:
        cancel_ad = driver.find_element(By.XPATH, '//*[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 f4552b6561"]').click()
    except:
        pass
        # print("There wasn't a second popup ad.")

    # = 98 entries

    count_entries = 95 # entries

    while count_entries < config["max_entries"]:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config["delay"])
        try:
            # Wait until the element appears
            load_more_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[span[text()='Load more results']]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_btn)
            time.sleep(config["delay"])
            load_more_btn.click()
            count_entries += 23
        except:
            break
            # print("Load more button did not appear within the timeout.")

    get_cards(driver, entries)

print()
print("-----------------------")
print("Search finished.")
print("Entering locations in excel files...")
print("-----------------------")
print("Name   Locations found")
start_date_str = start_date.strftime('%d_%B_%Y')
for p in places:
    data_locations = pd.DataFrame(entries[p], columns=['Name', 'Link', 'Price', 'Rating', 'Location'])
    data_locations.drop_duplicates()
    print(f"{p} {df.shape[0]}") # number of rows without duplicates
    try:
        with pd.ExcelWriter(f'data/{p}_{start_date_str}.xlsx', mode='a') as writer:
            data_locations.to_excel(writer, sheet_name=place)
    except:
        with pd.ExcelWriter(f'data/{p}_{start_date_str}.xlsx', mode='w') as writer:
            data_locations.to_excel(writer, sheet_name=place)

time.sleep(config["delay"])
# Close the driver
driver.quit()
