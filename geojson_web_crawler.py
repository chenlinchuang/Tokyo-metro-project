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

### Find relations id of every metro line
id_list = []

# Access urban area lines (x9) by url_browser
url_wiki = 'https://wiki.openstreetmap.org/wiki/Tokyo_Metro'
browser.get(url_wiki)
id_elem = browser.find_elements_by_class_name("plainlinks") # Plainlinks are element attributes of relations id
for id in id_elem:
    id_list.append(id.text)             # Text is the string attribute of relations

# Access suburb area metro lines (x4) by transfer link
browser.find_element_by_link_text('Tokyo Metropolitan Bureau of Transportation').click()
id_elem2 = browser.find_elements_by_class_name("plainlinks") # Plainlinks are element attributes of relations id
for id2 in id_elem2:
    id_list.append(id2.text)            # Text is the string attribute of relations

id_list = [id.lstrip() for id in id_list]

### Main code
# Access overpass api by url_browser
url_overpass = 'https://overpass-turbo.eu/'
browser.get(url_overpass)

# Css selector process to avoid textarea hidden caused by xpath
# Textarea is an attribute whose main function belongs to class div, name "CodeMirror"
search_elem = browser.find_element_by_css_selector("div.CodeMirror textarea")

# Delete preset code in textarea
search_elem.send_keys(Keys.CONTROL + "a")
search_elem.send_keys(Keys.DELETE)