from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from Scrapers.scraper import Scraper
from dateutil import relativedelta
import datetime as dt
from lxml import html
import numpy as np
import requests
import time


class RedditScraper(Scraper):
    _URL = r"https://www.reddit.com/r/"

    def __init__(self, subreddit: str, headers: dict = {'User-Agent': 'Mozilla/5.0'}):
        super(RedditScraper, self).__init__()
        self.subreddit = subreddit
        self._URL += self.subreddit
        self.headers = headers

    def get_date(self, post):
        """
        :param post: selenium element representing a reddit post
        :return: approximated date of the post
        """
        try:
            now = dt.datetime.now()
            self.wait_to_find(By.CLASS_NAME, "_3jOxDPIQ0KaOWpzvSQo-1s")
            txt = post.find_element_by_class_name("_3jOxDPIQ0KaOWpzvSQo-1s").text
            n, freq = txt.split(' ')[-2:]
            if freq in ('jour', 'jours', 'days', 'day'):
                date = now - relativedelta.relativedelta(days=int(n))
            elif freq in ('mois', 'month', 'months'):
                date = now - relativedelta.relativedelta(months=int(n))
            elif freq in ('année', 'années', 'an', 'ans', 'year', 'years'):
                date = now - relativedelta.relativedelta(years=int(n))
            elif freq in ('heure', 'heures', 'hours', 'hour'):
                date = now - relativedelta.relativedelta(hours=int(n))
            elif freq in ('minute', 'minutes'):
                date = now - relativedelta.relativedelta(minutes=int(n))
            elif freq in ('second', 'secondes', 'seconds'):
                date = now - relativedelta.relativedelta(seconds=int(n))
            else:
                date = txt
        except:
            date = np.nan
        return date

    def get_body(self, post):
        """
        :param post: selenium element representing a reddit post
        :return: text body of the post
        """
        b = self.get_from_attribute(post.find_elements_by_tag_name("a"), "data-click-id", ("body"))

        # use of request as selenium has some bugs
        url_full_post = b.get_attribute("href")
        page = requests.get(url=url_full_post, headers=self.headers)
        tree = html.fromstring(page.content)
        identifier = url_full_post.split('/')[6]

        try:
            body = " ".join(map(lambda x: x.text if x.text is not None else "",
                                tree.xpath(f'//*[@id="t3_{identifier}"]/div/div[5]/div')[0]))
        except:
            body = None

        return body

    @staticmethod
    def get_score(post):
        """
        :param post: selenium element representing a reddit post
        :return: score of the post
        """
        score = None
        try:
            score = int(post.find_element_by_class_name('_1rZYMD_4xY3gRcSS3p8ODO').text)
        except:
            try:
                score = int(post.find_element_by_class_name('_vaFo96phV6L5Hltvwcox').text)
            except:
                pass
        return score

    def formatted_posts(self, posts, ticker):
        """
        :param posts: list of posts
        :param ticker: ticker of the company to get information about
        :return: data extracted from the tweets organised into a list of dictionaries
        """
        data = list()
        for post in posts:
            data.append({
                "date": self.get_date(post),
                "ticker": ticker,
                "source": "Reddit/r/" + self.subreddit,
                "score": self.get_score(post),
                "account": post.find_element_by_class_name('_2tbHP6ZydRpjI44J3syuqC').text,
                "title": post.find_element_by_tag_name('h3').text,
                "text_content": self.get_body(post),
            })

        return data

    def get_posts(self, start_date: dt.datetime, ticker: str):
        """
        :param start_date: minimum date of interest
        :param ticker: ticker of the company to get information about
        :return: Scrolls on the page to load posts until dates of posts are before start_date
        return list of selenium element representing posts
        """

        # wait to load page
        time.sleep(self._PAUSE_TIME)

        posts = list()

        flag = True
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while flag:
            # new tweets
            self.wait_to_find(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
            new_post = self.driver.find_elements_by_class_name('_1oQyIsiPHYt6nx7VOmd1sz')[-1]

            # get last date
            last_date = self.get_date(new_post)

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

        new_posts = self.driver.find_elements_by_class_name('_1oQyIsiPHYt6nx7VOmd1sz')
        posts += self.formatted_posts(new_posts, ticker)

        return posts

    def sort_research_result(self):
        # wait until page has loaded
        time.sleep(self._PAUSE_TIME)

        try:
            button = self.driver.find_elements_by_tag_name("button")
            sort = self.get_from_attribute(button, "text", ("Trier", "Sort", "Classificar"))
        except:
            sort = self.driver.find_element_by_id('search-results-sort')

        sort.click()

        # wait until page has loaded
        self.wait_to_find(By.TAG_NAME, "button")

        # ... by new
        self.get_from_attribute(self.driver.find_elements_by_tag_name("button"), 'text', ('New')).click()

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
    tickers = ['TSLA']
    end_date = dt.datetime.now()
    start_date = end_date - relativedelta.relativedelta(days=1)

    scraper = RedditScraper(subreddit)
    res = scraper.get(tickers, start_date, end_date)
