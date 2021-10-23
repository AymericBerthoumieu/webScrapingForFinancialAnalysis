from selenium import webdriver
import pandas as pd
import datetime as dt
from collections.abc import Iterable
from selenium.webdriver.support.ui import WebDriverWait
from Utils.exceptions import NoSuchElementException, TimeoutException


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

    def wait_to_find(self, by_variable, attribute):
        """
        :param by_variable: variable to look for
        :param attribute: attribute of the variable
        Wait until the page is loaded to find the element required.
        Raise an exception in case the element is not found or if the program takes to much time
        """
        try:
            WebDriverWait(self.driver, 20).until(lambda x: x.find_element(by=by_variable, value=attribute))
        except (NoSuchElementException, TimeoutException):
            print(f'{by_variable} {attribute} have not been found in the web page.')
            self.driver.quit()

    def do_research(self, ticker: str, start_date: dt.datetime):
        """
        :param end_date: maximum date of interest
        :param start_date: minimum date of interest
        :param ticker: ticker of the company to get information about
        :return: formatted information about ticker between start_date and end_date
        """
        raise NotImplemented

    def get_info(self, tickers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
        """
        :param tickers: list of tickers to get information about
        :param start_date: minimum date of interest
        :param end_date: maximum date of interest
        :return: formatted information about all tickers between start_date and end_date
        """
        # connection to the explore page
        self.connection(self._URL)

        # gather information on each ticker
        info = list()
        for ticker in tickers:
            info += self.do_research(ticker, start_date)

        # close driver
        self.driver.quit()

        info_df = pd.DataFrame(info)
        info_df = info_df[start_date < info_df.date]
        info_df = info_df[info_df.date < end_date]
        return info_df