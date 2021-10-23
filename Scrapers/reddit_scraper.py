from selenium.webdriver.common.keys import Keys
from Utils.exceptions import NotFoundException
from selenium.webdriver.common.by import By
from Scrapers.scraper import Scraper
import datetime as dt


class RedditScraper(Scraper):
    _URL = r"https://www.reddit.com/r/"

    def __init__(self, subreddit: str):
        super(RedditScraper, self).__init__()
        self.subreddit = subreddit
        self._URL += self.subreddit

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

        # wait until page has loaded
        self.wait_to_find(By.TAG_NAME, "a")

        # focus on most recent tweets
        a = self.driver.find_elements_by_tag_name("a")

        i = 0
        while i < len(a) and '=live' not in a[i].get_attribute('href'):
            i += 1

        if i == len(a):
            raise NotFoundException("Could manage to find the 'recent' link.")
        else:
            a[i].click()

        # get information from tweet
        posts = self.get_posts(start_date, ticker)

        return posts


if __name__ == '__main__':
    subreddit = "wallstreetbets"
    tickers = ["AAPL"]

    scraper = RedditScraper(subreddit)
    res = scraper.get_info(tickers)