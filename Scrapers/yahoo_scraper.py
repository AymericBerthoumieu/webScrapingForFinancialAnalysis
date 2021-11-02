from Utils.decorators import time_elapsed
from collections.abc import Iterable
from Scrapers.scraper import Scraper
import datetime as dt
import pandas as pd
import warnings
import time


class YahooScraper(Scraper):
    _URL = r"https://fr.finance.yahoo.com/quote/{}/history?p={}"

    def __init__(self):
        super(YahooScraper, self).__init__()

    def get_prices(self, ticker: str, start_date: dt.datetime, end_date: dt.datetime):
        """
        :param ticker:
        :param start_date:
        :param end_date:
        :return:
        """
        # load historical data page
        self.connection(self._URL.format(ticker, ticker))

        # reject cookies
        try:
            time.sleep(self._PAUSE_TIME)
            self.driver.find_element_by_name('reject').click()
        except:
            pass

        time.sleep(self._PAUSE_TIME)

        # select the good range date
        span = self.driver.find_elements_by_tag_name("span")
        i = 0
        s = span[i]
        while i < len(span) and s.get_attribute('class') != "C($linkColor) Fz(14px)":
            i += 1
            s = span[i]
        s.click()

        # input start and end date
        self.wait_to_find("name", "startDate")
        start = self.driver.find_element_by_name("startDate")
        start.send_keys(start_date.strftime("%d/%m/%Y"))
        end = self.driver.find_element_by_name("endDate")
        end.send_keys(end_date.strftime("%d/%m/%Y"))
        self.driver.find_element_by_id("dropdown-menu").find_elements_by_tag_name("button")[-2].click()

        # send request
        self.driver.find_elements_by_tag_name("button")[-1].click()
        time.sleep(self._PAUSE_TIME)

        # find downloading link
        a = self.driver.find_elements_by_tag_name("a")
        i = 0
        while i < len(a) and a[i].get_attribute('download') == "":
            i += 1

        data = pd.read_csv(a[i].get_attribute("href"))
        data.Date = pd.to_datetime(data.Date)
        data['ticker'] = ticker
        return data

    @time_elapsed
    def get(self, tickers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
        """
        :param tickers:
        :param start_date:
        :param end_date:
        :return:
        """
        res = pd.DataFrame()

        for ticker in tickers:
            try:
                res = pd.concat((res, self.get_prices(ticker, start_date, end_date)))
            except:
                warnings.warn(f'Error while loading {ticker}.')

        self.driver.quit()
        return res


if __name__ == '__main__':
    from dateutil import relativedelta

    tickers = ['^NDX']
    end_date = dt.datetime.now() - dt.timedelta(days=1)
    start_date = end_date - relativedelta.relativedelta(months=6)

    scraper = YahooScraper()
    res = scraper.get(tickers, start_date, end_date)
