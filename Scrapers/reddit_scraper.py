from selenium.webdriver.common.keys import Keys
from Utils.exceptions import NotFoundException
from selenium.webdriver.common.by import By
from Scrapers.scraper import Scraper
import datetime as dt
import time


class RedditScraper(Scraper):
    _URL = r"https://www.reddit.com/r/"

    def __init__(self, subreddit: str):
        super(RedditScraper, self).__init__()
        self.subreddit = subreddit
        self._URL += self.subreddit

    def get_posts(self, start_date, ticker):
        pass

    def sort_research_result(self):
        # wait until page has loaded
        time.sleep(self._PAUSE_TIME)

        try:
            button = self.driver.find_elements_by_tag_name("button")

            i = 0
            while i < len(button) and button[i].text not in ('Trier', 'Sort'):
                i += 1

            if i == len(button):
                raise NotFoundException("Could manage to find the 'Sort' button.")

            sort = button[i]
        except:
            sort = self.driver.find_element_by_id('search-results-sort')

        sort.click()

        # wait until page has loaded
        self.wait_to_find(By.TAG_NAME, "button")

        # ... by new
        a = self.driver.find_elements_by_tag_name("button")

        i = 0
        while i < len(a) and a[i].text != 'New':
            i += 1

        if i == len(a):
            raise NotFoundException("Could manage to find the 'New' button.")
        else:
            a[i].click()

    def do_research(self, ticker: str, start_date: dt.datetime):
        """
        :param end_date: maximum date of interest
        :param start_date: minimum date of interest
        :param ticker: ticker of the company to get information about
        :return: formatted tweets about ticker between start_date and end_date
        """
        # wait until page has loaded
        self.wait_to_find(By.TAG_NAME, "input")

        # do the search in search bar
        search_bar = self.driver.find_element_by_tag_name('input')
        search_bar.send_keys(Keys.CONTROL, "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(ticker, Keys.ENTER)

        # focus on most recent tweets
        # sort by new
        self.sort_research_result()

        # get information from tweet
        posts = self.get_posts(start_date, ticker)

        return posts


if __name__ == '__main__':
    subreddit = "wallstreetbets"
    tickers = ["AAPL"]
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(hours=3)

    scraper = RedditScraper(subreddit)
    res = scraper.get_info(tickers, start_date, end_date)
