from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from Utils.decorators import time_elapsed
from collections.abc import Iterable
from Scrapers.scraper import Scraper
import datetime as dt
import numpy as np
import getpass
import time


class TwitterScraper(Scraper):
    _URL_EXPLORE = r"https:twitter.com/explore"
    _URL = r"https:twitter.com/home"
    _CASH_TAG = "$"
    _HASH_TAG = "#"

    def __init__(self, username=None, password=None):
        super(TwitterScraper, self).__init__()
        self.username = username
        self.password = password

    def connection(self, url):
        """
        Open connection.
        """
        # open the URL
        self.driver.get(url)

        # connect the profile to avoid to be disturbed
        self.connection_to_account()

        time.sleep(self._PAUSE_TIME)
        # go to explore
        self.driver.get(self._URL_EXPLORE)

    def connection_to_account(self):
        """
        Open connection to a tweeter account.
        """
        self.wait_to_find('name', 'username')
        # get element for email and post the username
        email = self.driver.find_element(by='name', value='username')
        if self.username is None:
            self.username = input("Please enter your Twitter e-mail address:")
        email.send_keys(self.username, Keys.ENTER)

        # wait for the page to actualise
        self.wait_to_find(By.TAG_NAME, 'input')
        input_field = self.driver.find_element(by=By.TAG_NAME, value='input')
        if input_field.get_attribute('name') != 'password':
            print('Your behaviour triggered Twitter security, please enter your phone number in the browser.')
            time.sleep(self._PAUSE_TIME)

        # wait for the page to actualise
        self.wait_to_find('name', "password")

        # get element for password and post the password
        password = self.driver.find_element(by='name', value='password')
        if self.password is None:
            self.password = getpass.getpass("Please enter your Twitter password:")
        password.send_keys(self.password, Keys.ENTER)

    def get_date(self, tweet):
        """
        :param tweet: selenium element representing a tweet
        :return: date of the tweet
        """
        try:
            self.wait_to_find(By.TAG_NAME, 'time')
            date = dt.datetime.strptime(tweet.find_element_by_tag_name('time').get_attribute('datetime')[:-5],
                                        "%Y-%m-%dT%H:%M:%S")
        except:
            try:  # very long internet connection
                time.sleep(self._PAUSE_TIME + 3)
                date = dt.datetime.strptime(tweet.find_element_by_tag_name('time').get_attribute('datetime')[:-5],
                                            "%Y-%m-%dT%H:%M:%S")
            except:
                date = np.nan
        return date

    def get_tweets(self, start_date: dt.datetime, ticker: str):
        """
        :param start_date: minimum date of interest
        :param ticker: ticker of the company to get information about
        :return: Scrolls on the page to load tweets until dates of tweets are before start_date
        return list of selenium element representing tweets
        """
        # wait to load page
        time.sleep(self._PAUSE_TIME)

        tweets = list()

        flag = True
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while flag:
            # new tweets
            new_tweets = self.driver.find_element_by_tag_name('section').find_elements_by_tag_name('article')
            tweets += self.formatted_tweets(new_tweets, ticker)

            # get last date
            last_date = self.get_date(new_tweets[-1])

            # scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            # wait to load page
            time.sleep(self._PAUSE_TIME)
            # calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # break condition
            if last_date < start_date or new_height == last_height:
                flag = False
            last_height = new_height

        return tweets

    @staticmethod
    def get_account_name(tweet):
        """
        :param tweet: selenium element representing a tweet
        :return: the account that has posted the tweet
        """
        try:
            span = tweet.find_elements_by_tag_name('span')
            acc = TwitterScraper.get_from_attribute_reverse(span, 'text', '@')
            res = acc.text
        except:
            res = ""
        return res

    @staticmethod
    def get_text_content(tweet):
        """
        :param tweet: selenium element representing a tweet
        :return: the text content of the tweet. tag and link are to tricky to extract at the moment.
        """
        try:
            res = list()
            l = tweet.find_elements_by_tag_name('span')
            i = 0
            while i < len(l) and not '@' in l[i].text:
                i += 1
            i += 1
            for j in range(i, len(l)):
                res.append(l[j].text)
        except:
            res = list()

        return " ".join(res)

    def formatted_tweets(self, tweets: Iterable, ticker: str):
        """
        :param tweets: list of tweets
        :param ticker: ticker of the company to get information about
        :return: data extracted from the tweets organised into a list of dictionaries
        """
        data = list()
        for tweet in tweets:
            try:
                account = self.get_account_name(tweet)
            except:
                account = 'unknown'

            try:
                content = self.get_text_content(tweet)
            except:
                content = 'unknown'

            data.append({
                "date": self.get_date(tweet),
                "ticker": ticker,
                "source": "Twitter",
                "account": account,
                "text_content": content,
            })

        return data

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

        # if a connection is required
        search_bar.send_keys(Keys.CONTROL, "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(ticker, Keys.ENTER)

        # wait until page has loaded
        self.wait_to_find(By.TAG_NAME, "a")

        # focus on most recent tweets
        a = self.driver.find_elements_by_tag_name("a")
        self.get_from_attribute_reverse(a, 'href', '=live').click()

        # get information from tweet
        time.sleep(self._PAUSE_TIME)
        tweets = self.get_tweets(start_date, ticker)

        return tweets

    @time_elapsed
    def get(self, tickers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
        """
        :param tickers: list of tickers to get information about
        :param start_date: minimum date of interest
        :param end_date: maximum date of interest
        :return: formatted tweets about all tickers between start_date and end_date
        """
        return super(TwitterScraper, self).get(map((lambda x: self._CASH_TAG + x), tickers), start_date, end_date)


if __name__ == "__main__":
    from Utils.const import TICKER_INFLUENCE
    from dateutil import relativedelta

    tickers = TICKER_INFLUENCE
    end_date = dt.datetime.now()
    # I have an offset of 2 hours between my time and twitter time
    start_date = end_date - relativedelta.relativedelta(months=6)

    scraper = TwitterScraper()
    res = scraper.get(tickers, start_date, end_date)
