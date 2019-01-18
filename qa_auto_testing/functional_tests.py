from selenium import webdriver

browser = webdriver.Chrome()
browser.get('http://127.0.0.1:8000/')
print(browser.title)
assert 'CPH Indicator Visualization Tool' in browser.title