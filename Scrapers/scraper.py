from Utils.exceptions import NoSuchElementException, TimeoutException, NotFoundException
from selenium.webdriver.support.ui import WebDriverWait
from Utils.decorators import time_elapsed
from collections.abc import Iterable
from selenium import webdriver
import datetime as dt
import pandas as pd


class Scraper:
    # can depends on the internet connection. The lower the connection, the higher the pause time should be
    _PAUSE_TIME = 1
    _URL = ""

    def __init__(self):
        # disable notification
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('disable-notifications')

        # Chrome will be used to navigate
        self.driver = webdriver.Chrome('../Utils/chromedriver.exe', options=chrome_options)

    def connection(self, url):
        """
        Open connection.
        """
        # open the URL
        self.driver.get(url)

    @staticmethod
    def get_from_attribute(element, name: str, values: Iterable):
        """
        :param element: element in which the research will be done
        :param name: name of the attribute
        :param values: value of the attribute
        :return: first element with attribute matching value
        """
        i = 0

        if name != 'text':
            while i < len(element) and (element[i].get_attribute(name) is None or element[i].get_attribute(
                    name) not in values):
                i += 1
        else:
            while i < len(element) and (element[i].text == "" or element[i].text not in values):
                i += 1

        if i == len(element):
            raise NotFoundException(f"Element with attribute {name} in {values} not found.")
        else:
            found = element[i]
        return found

    @staticmethod
    def get_from_attribute_reverse(element, name: str, value: Iterable):
        """
        :param element: element in which the research will be done
        :param name: name of the attribute
        :param value: value of the attribute
        :return: first element with value in attribute
        """
        i = 0

        if name != 'text':
            while i < len(element) and value not in element[i].get_attribute(name):
                i += 1
        else:
            while i < len(element) and value not in element[i].text:
                i += 1

        if i == len(element):
            raise NotFoundException(f"Element with {value} in attribute {name} not found.")
        else:
            found = element[i]
        return found

    def wait_to_find(self, by_variable, attribute, wait=20):
        """
        :param by_variable: variable to look for
        :param attribute: attribute of the variable
        :param wait: waiting time
        Wait until the page is loaded to find the element required.
        Raise an exception in case the element is not found or if the program takes to much time
        """
        try:
            WebDriverWait(self.driver, wait).until(lambda x: x.find_element(by=by_variable, value=attribute))
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

    @time_elapsed
    def get(self, tickers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
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
            try:
                info += self.do_research(ticker, start_date)
            except:
                pass

        # close driver
        self.driver.quit()

        info_df = pd.DataFrame(info)
        info_df.date = info_df.date.ffill()
        info_df = info_df[start_date < info_df.date]
        info_df = info_df[info_df.date < end_date]
        return info_df
