"""
This file will be used to setup the functions required to run the tests
The code was adopted from https://github.com/Rhoynar/python-selenium-bdd

Modified by: Jean-Marie

"""
# Selenium is required for the webdriver to function
from selenium import webdriver
from features.test_config.config import settings
from urllib.parse import urljoin

class Setup:
	instance = None

	@classmethod
	def get_instance(cls):
		if cls.instance is None:
			cls.instance = Setup()
		return cls.instance

	def __init__(self):
		if str(settings['browser']).lower() is "firefox":
			self.driver = webdriver.Firefox()
		elif str(settings['browser']).lower() is "chrome":
			self.driver = webdriver.Chrome()
		else:
			self.driver = webdriver.Firefox()

	def get_driver(self):
		'''
		:return: returns the webdriver - chrome of firefox
		'''
		return self.driver

	def load_website(self):
		'''
		:return: The main website
		'''
		self.driver.get(settings['url'])

	def goto_page(self, page):
		'''
		:param page: the url to the page being tested
		:return: returns the page the QA specifies
		'''
		self.driver.get(urljoin(settings['url'], page.lower()))

	def verify_component_exists(self, component):
		'''
		:param component: is the item the QA will be searching for on a page such as a button or text
		:return: True if the item is found else the test fails
		'''
		# Simple implementation
		assert component in self.driver.find_element_by_tag_name('body').text, \
        "Component {} not found on page".format(component)

cph_ivt_app = Setup.get_instance()
