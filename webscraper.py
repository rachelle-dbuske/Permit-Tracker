# import the required library
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

#inputs
permittype = "Inyo National Forest - Wilderness Permits"
entry_point = "George Lake"
groupsize = 5
startmonth = "3"
startday = "28"
startyear = "2025"

# Uncomment for headless mode and remove following line of code
# instantiate a Chrome options object
options = webdriver.ChromeOptions()

# set the options to use Chrome in headless mode
options.add_argument("--headless=new")
 
# initialize an instance of the Chrome driver (browser) in headless mode
driver = webdriver.Chrome(options=options)

#uncomment for non headless mode
# initialize an instance of the chrome driver (browser) - remove this for headless operation
#driver = webdriver.Chrome()

# visit your target site
driver.get("https://www.recreation.gov/")

'''
# wait up to 10 seconds until the document is fully ready
WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)
'''
time.sleep(3)

# area input
area_input = driver.find_element(By.ID, "hero-search-input")
area_input.send_keys(permittype)

# search button
search_button = driver.find_element(By.CSS_SELECTOR, "button.sarsa-button.sarsa-button-primary.sarsa-button-md.nav-search-button")
search_button.click()

# select permit type
#   this code bypasses the overlapped items
link_element = driver.find_element(By.PARTIAL_LINK_TEXT, permittype)
actions = ActionChains(driver)
actions.move_to_element(link_element).click().perform()

# Switch to the new tab
original_window = driver.current_window_handle # Store the current window handle
new_window = [window for window in driver.window_handles if window != original_window][0]
driver.switch_to.window(new_window)

# select explore available permits
button_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@title='Explore Available Permits']"))
)
button_element.click()

# select commercial guides trip
radio_button = driver.find_element(By.ID, "prompt-answer-no1")
radio_button.click()

# select permit type
# Locate the dropdown element
dropdown_element = driver.find_element(By.ID, "permit-type")  # Replace with the correct ID
# Create a Select object
select = Select(dropdown_element)
# Select the option with value "overnight-permit"
select.select_by_value("overnight-permit")

# select group members
# Wait for the span element with the class "rec-select-label" to be clickable
select_label = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[@class='rec-select-label' and text()='Add Group Members...']"))
)
# Click on the span element to open the dropdown
select_label.click()
# Wait for the input field inside the dropdown to be visible
input_field = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "guest-counter-number-field-People"))
)
# Enter the desired number into the input field (e.g., 5)
input_field.clear()  # Clear any existing value
input_field.send_keys(1) #always input 1 so you can extract # available, if groupsize is larger than available then it will say not available
# Close popup window
close_button = driver.find_element(By.XPATH, "//div[@class='sarsa-dropdown-base-popup-actions']//button[span//text()='Close']")
close_button.click()

# select date
# Wait for the month div to be clickable
month_div = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='month, ']"))
)
month_div.click()  # Focus on the month input
month_div.send_keys(startmonth)  # Enter the new month value
# select the day div
day_div = driver.find_element(By.XPATH, "//div[@aria-label='day, ']")
day_div.send_keys(startday)  # Enter the new day value
# select the year div
year_div = driver.find_element(By.XPATH, "//div[@aria-label='year, ']")
year_div.send_keys(startyear)  # Enter the new year value

#check for availability
# Locate the row with the entry point
target_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, f"//button[normalize-space(@aria-label)='{entry_point}']/ancestor::div[@data-component='Row']")
))

# Once the target row is found, check if open, NR, or 0
availability = target_row.find_element(
    By.CSS_SELECTOR, ".sarsa-button.sarsa-button-subtle.sarsa-button-md.rec-availability-date"
)
availability_data = availability.get_attribute("aria-label")

# Extract the people number from the aria-label or the span inside the button
if "People:" in availability_data:
    people_count = availability_data.split("People:")[1].split("out")[0].strip()
    people_count = people_count.replace('+', '') # Remove the '+' symbol if present
    if int(people_count) >= groupsize:
        print(f"Permit available for up to {people_count} starting on {startmonth}/{startday}/{startyear}")
    else:
        print(f"Only {people_count} spot(s) open.")
elif "No online reservations available" in availability_data:
    print("No online reservations available.")
elif "This permit is not yet released (NR).  Click NR to learn more." in availability_data:
    print("This permit is not yet released (NR).")
else:
    print("Error.")


# release the resources allocated by Selenium and shut down the browser
driver.quit()
