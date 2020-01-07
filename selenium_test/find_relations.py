from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
driverPath = 'geckodriver.exe'
browser = webdriver.Firefox(executable_path = driverPath)


print(id_list())

