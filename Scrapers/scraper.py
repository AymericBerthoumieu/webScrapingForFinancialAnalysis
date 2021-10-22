from selenium import webdriver


class Scraper:
    _URL = ""

    def __init__(self):
        # Chrome will be used to connect to Twitter
        self.driver = webdriver.Chrome('chromedriver.exe')

    def connection(self, url):
        """
        Open connection to a tweeter account.
        """
        # open the URL
        self.driver.get(url)
