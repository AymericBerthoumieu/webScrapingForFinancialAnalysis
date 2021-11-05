from DataAnalysis.sentiment_return_correlation import SentimentReturnCorrelation
from DataAnalysis.sentiment_analysis_light import SentimentAnalysisLight
from Scrapers.twitter_scraper import TwitterScraper
from DataAnalysis.data_cleaner import DataCleaner
from Scrapers.reddit_scraper import RedditScraper
from Scrapers.yahoo_scraper import YahooScraper
from collections.abc import Iterable
from Utils.const import SUBREDDITS
from dateutil import relativedelta
import datetime as dt
import pandas as pd

PATH_TO_OLD_POSTS = '../Utils/old_reddit_posts.csv'
PATH_TO_LEVELS = '../Utils/levels.csv'
PATH_TO_TWEETS = '../Utils/old_tweets.csv'
PATH_TO_FULL_DATA = '../Utils/full_data.csv'


def load_reddit_posts(influencers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
    """
    :param influencers: Tickers of the stocks we want to study the influence on the index
    :param start_date: lower bound of interest
    :param end_date: upper bound of interest
    :return: reddit posts
    """
    # get reddit posts
    posts = pd.DataFrame()
    for sub in SUBREDDITS:
        print(f"Extracting posts from {sub}")
        try:
            scraper = RedditScraper(subreddit=sub)
            new_posts = scraper.get(influencers, start_date, end_date)
            if new_posts.size > 0:
                posts = pd.concat((posts, new_posts))
        except:
            print(f"Error while trying to get posts from {sub}")

    # prepare posts
    posts.set_index('date', inplace=True)
    posts['title'].fillna('', inplace=True)
    posts['text_content'].fillna('', inplace=True)
    posts['full'] = posts['title'] + ' ' + posts['text_content']
    posts = posts.rename({'score': 'weights'}, axis=1)
    posts.index = pd.to_datetime(posts.index)
    posts.to_csv(PATH_TO_OLD_POSTS)
    return posts


def load_yahoo_level(reference: str, start_date: dt.datetime, end_date: dt.datetime):
    """
    :param reference: Ticker of the index
    :param start_date: lower bound of interest
    :param end_date: upper bound of interest
    :return: levels of the index
    """
    scraper = YahooScraper()
    levels = scraper.get([reference], start_date, end_date).set_index('Date')
    levels.to_csv(PATH_TO_LEVELS)
    return levels


def load_tweets(influencers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
    """
    :param influencers: Tickers of the stocks we want to study the influence on the index
    :param start_date: lower bound of interest
    :param end_date: upper bound of interest
    :return: tweets
    """
    # get tweets
    scraper = TwitterScraper()

    print(f"Extracting tweets")
    try:
        tweets = scraper.get(influencers, start_date, end_date)

        # prepare posts
        tweets.set_index('date', inplace=True)
        tweets['full'] = tweets['text_content'].fillna('')
        tweets.index = pd.to_datetime(posts.index)
        tweets.to_csv(PATH_TO_TWEETS)
    except:
        print(f"Error while trying to get tweets")
        tweets = pd.DataFrame()

    return tweets


def pipeline_direct(reference: str, influencers: Iterable):
    """
    :param reference: Ticker of the index
    :param influencers: Tickers of the stocks we want to study the influence on the index
    :return: sentiment correlation
    """
    end_date = dt.datetime.now()
    start_date = end_date - relativedelta.relativedelta(months=1)

    # get reference levels
    levels = load_yahoo_level(reference, start_date, end_date)

    # get reddit posts
    posts = load_reddit_posts(influencers, start_date, end_date)

    # clean posts
    cleaner = DataCleaner()
    posts['full_clean'] = posts.full.apply(lambda x: cleaner.run(x))

    # sentiment analysis on posts
    analyser = SentimentAnalysisLight()
    posts['score'] = analyser.predict(posts['full_clean'])

    # correlation between sentiment and results
    corr_analyser = SentimentReturnCorrelation(correlation_method='sign')
    correlation_sign = corr_analyser.run(posts, levels)
    corr_analyser.set_correlation_method('pearson')
    correlation_pearson = corr_analyser.run(posts, levels).iloc[0, 1]  # only takes one factor

    return correlation_pearson, correlation_sign


def pipeline_from_csv(path=PATH_TO_OLD_POSTS):
    """
    :return: sentiment correlation
    """
    end_date = dt.datetime.now()
    start_date = end_date - relativedelta.relativedelta(months=1)

    # get reference levels
    levels = pd.read_csv(PATH_TO_LEVELS, index_col=0)
    levels.index = pd.to_datetime(levels.index)

    # get reddit posts
    posts = pd.read_csv(path, index_col=0)
    posts.index = pd.to_datetime(posts.index)

    # clean posts
    cleaner = DataCleaner()
    posts['full_clean'] = posts.full.apply(lambda x: cleaner.run(x))

    # sentiment analysis on posts
    analyser = SentimentAnalysisLight()
    posts['score'] = analyser.predict(posts['full_clean'])

    # correlation between sentiment and results
    corr_analyser = SentimentReturnCorrelation(correlation_method='sign')
    correlation_sign = corr_analyser.run(posts, levels)
    corr_analyser.set_correlation_method('pearson')
    correlation_pearson = corr_analyser.run(posts, levels).iloc[0, 1]  # only takes one factor

    return correlation_pearson, correlation_sign


def full_load_to_csv(reference: str, influencers: Iterable, start_date: dt.datetime, end_date: dt.datetime):
    """
    :param reference: Ticker of the index
    :param influencers: Tickers of the stocks we want to study the influence on the index
    :param start_date: lower bound of interest
    :param end_date: upper bound of interest
    :return: sentiment correlation
    """
    cleaner = DataCleaner()

    # levels
    levels = load_yahoo_level(reference, start_date, end_date)

    # reddit
    posts = load_reddit_posts(influencers, start_date, end_date)
    posts['full_clean'] = posts.full.apply(lambda x: cleaner.run(x))

    # tweeter
    tweets = load_tweets(influencers, start_date, end_date)
    tweets['full_clean'] = tweets.full.apply(lambda x: cleaner.run(x))

    full_data = pd.concat((posts, tweets))
    full_data.to_csv(PATH_TO_FULL_DATA)


if __name__ == '__main__':
    from Utils.const import TICKERS_INFLUENCE

    reference = '^NDX'
    influencers = TICKERS_INFLUENCE
    end_date = dt.datetime.now()
    start_date = end_date - relativedelta.relativedelta(months=1)

    load_yahoo_level(reference, start_date, end_date)
    load_reddit_posts(['AAPL', 'FB'], start_date, end_date)
    corr_pearson, corr_sign = pipeline_from_csv()
    print(corr_sign, corr_pearson)
