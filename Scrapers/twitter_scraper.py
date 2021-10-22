import time
import pandas as pd
import datetime as dt
from Scrapers.scraper import Scraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from Utils.exceptions import NoSuchElementException, TimeoutException, NotFoundException


class TwitterScraper(Scraper):
    _URL = r"https:twitter.com/home"
    _URL_EXPLORE = r"https:twitter.com/explore"
    # can depends on the internet cnnection. The lower the connection, the higher the pause time should be
    _SCROLL_PAUSE_TIME = 1
    _CASH_TAG = "$"
    _HASH_TAG = "#"

    def __init__(self, username=None, password=None):
        super(TwitterScraper, self).__init__()
        self.username = username
        self.password = password

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

    def connection_to_account(self):
        """
        Open connection to a tweeter account.
        """
        self.connection(self._URL)

        # wait until page has loaded
        self.wait_to_find('name', "username")

        # get element for email and post the username
        email = self.driver.find_element(by='name', value='username')
        if self.username is None:
            self.username = input("Please enter your Twitter e-mail address:")
        email.send_keys(self.username, Keys.ENTER)

        # wait for the page to actualise
        self.wait_to_find('name', "password")

        # get element for password and post the password
        password = self.driver.find_element(by='name', value='password')
        if self.password is None:
            self.password = input("Please enter your Twitter e-mail address:")
        password.send_keys(self.password, Keys.ENTER)

    def get_tweets(self, start_date: dt.datetime, ticker: str):
        """
        :param start_date: minimum date of interest
        :param ticker: ticker of the company to get information about
        :return: Scrolls on the page to load tweets until dates of tweets are before start_date
        return list of selenium element representing tweets
        """
        # wait to load page
        time.sleep(self._SCROLL_PAUSE_TIME)

        tweets = list()

        flag = True
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while flag:
            # new tweets
            new_tweets = self.driver.find_element_by_tag_name('section').find_elements_by_tag_name('article')
            tweets += self.formatted_tweets(new_tweets, ticker)

            # get last date
            last_date = dt.datetime.strptime(
                new_tweets[-1].find_element_by_tag_name('time').get_attribute('datetime')[:-5],
                "%Y-%m-%dT%H:%M:%S")

            # scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            # wait to load page
            time.sleep(self._SCROLL_PAUSE_TIME)
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
        l = tweet.find_elements_by_tag_name('span')
        i = 0
        while i < len(l) and not '@' in l[i].text:
            i += 1
        return l[i].text

    @staticmethod
    def get_text_content(tweet):
        """
        :param tweet: selenium element representing a tweet
        :return: the text content of the tweet. tag and link are to tricky to extract at the moment.
        """
        res = list()
        l = tweet.find_elements_by_tag_name('span')
        i = 0
        while i < len(l) and not '@' in l[i].text:
            i += 1
        i += 1
        for j in range(i, len(l)):
            res.append(l[j].text)

        return " ".join(res)

    @staticmethod
    def formatted_tweets(tweets: list, ticker: str):
        """
        :param tweets: list of tweets
        :param ticker: ticker of the company to get information about
        :return: data extracted from the tweets organised into a list of dictionaries
        """
        data = list()
        for tweet in tweets:
            try:
                account = TwitterScraper.get_account_name(tweet)
            except:
                account = 'unknown'

            try:
                content = TwitterScraper.get_text_content(tweet)
            except:
                content = 'unknown'

            data.append({
                "date": dt.datetime.strptime(tweet.find_element_by_tag_name('time').get_attribute('datetime')[:-5],
                                             "%Y-%m-%dT%H:%M:%S"),
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
        tweets = self.get_tweets(start_date, ticker)

        return tweets

    def get_info(self, tickers: list, start_date: dt.datetime, end_date: dt.datetime):
        """
        :param tickers: list of tickers to get information about
        :param start_date: minimum date of interest
        :param end_date: maximum date of interest
        :return: formatted tweets about all tickers between start_date and end_date
        """
        # connection to the explore page
        self.connection(self._URL_EXPLORE)

        # gather information on each ticker
        tweets = list()
        for ticker in tickers:
            tweets += self.do_research(self._CASH_TAG + ticker, start_date)

        # close driver
        self.driver.quit()

        tweets_df = pd.DataFrame(tweets)
        tweets_df = tweets_df[start_date < tweets_df.date]
        tweets_df = tweets_df[tweets_df.date < end_date]
        return tweets_df


if __name__ == "__main__":
    tickers = ["AAPL", "FB"]
    end_date = dt.datetime.now()
    # I have an offset of 2 hours between my time and twitter time
    start_date = end_date - dt.timedelta(hours=3)

    scraper = TwitterScraper()
    res = scraper.get_info(tickers, start_date, end_date)
