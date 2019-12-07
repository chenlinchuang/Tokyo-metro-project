from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Add driver
driverPath = 'geckodriver.exe'
# Set preference for geojson download
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.dir', 'g:\\')
profile.set_preference('browser.download.folderList', 0)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
# Set browser
browser = webdriver.Firefox(executable_path = driverPath, firefox_profile=profile)