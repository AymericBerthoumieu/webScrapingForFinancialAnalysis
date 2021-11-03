from DataAnalysis.sentiment_return_correlation import SentimentReturnCorrelation
from DataAnalysis.sentiment_analysis_light import SentimentAnalysisLight
from Scrapers.reddit_scraper import RedditScraper
from Scrapers.yahoo_scraper import YahooScraper
from collections.abc import Iterable
from Utils.const import SUBREDDITS
from dateutil import relativedelta
import datetime as dt
import pandas as pd

PATH_TO_OLD_POSTS = '../Utils/old_reddit_posts.csv'


def main(reference: str, influencers: Iterable):
    """
    :param reference: Ticker of the index
    :param influencers: Tickers of the stocks we want to study the influence on the index
    :return: sentiment correlation
    """
    end_date = dt.datetime.now()
    start_date = end_date - relativedelta.relativedelta(months=1)

    # get reference levels
    scraper = YahooScraper()
    levels = scraper.get([reference], start_date, end_date).set_index('Date')

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

    # sentiment analysis on posts
    analyser = SentimentAnalysisLight()
    posts['score'] = analyser.predict(posts['full'])

    # correlation between sentiment and results
    corr_analyser = SentimentReturnCorrelation(correlation_method='sign')
    correlation_sign = corr_analyser.run(posts, levels)
    corr_analyser.set_correlation_method('pearson')
    correlation_pearson = corr_analyser.run(posts, levels)

    return correlation_pearson, correlation_sign


if __name__ == '__main__':
    from Utils.const import TICKERS_INFLUENCE
    reference = '^NDX'
    influencers = TICKERS_INFLUENCE

    corr_sign, corr_pearson = main(reference, influencers)
    print(corr_sign, corr_pearson)