import pandas as pd
from numpy import sign


def sign_correlation(df_scores_returns: pd.DataFrame):
    """
    :param df_scores_returns: dataframe containing the daily return and the corresponding sentiment score
    :return: sign correlation (if a positive sentiment drives a positive return)
    The returns should be shifted so that we look if the sentiment of the previous day influence the day of
    interest.
    """
    df_scores_returns.fillna(0)
    score_sign = sign(df_scores_returns.final_score)
    returns_sign = sign(df_scores_returns.returns)
    return (score_sign * returns_sign).sum() / df_scores_returns.shape[0]


def pearson_correlation(df_scores_returns: pd.DataFrame):
    """
    :param df_scores_returns: dataframe containing the daily return and the corresponding sentiment score
    :return: pearson correlation
    The returns should be shifted so that we look if the sentiment of the previous day influence the day of
    interest.
    """
    df_scores_returns.fillna(0)
    return df_scores_returns[['returns', 'final_score']].corr()


CORRELATION_METHODS = {
    'sign': sign_correlation,
    'pearson': pearson_correlation
}


class SentimentReturnCorrelation:

    def __init__(self, correlation_method: str = 'sign'):
        """
        :param correlation_method: method used to compute the correlation
        """
        self._correlation_method = CORRELATION_METHODS[correlation_method]

    @staticmethod
    def score_by_day(df_scores: pd.DataFrame):
        """
        :param df_scores: df containing scores, dates (index) and weights (optional)
        :return: weighted score by day
        """
        # computes the weights
        if "weights" not in df_scores.columns:
            df_scores['weights'] = 1
        else:
            df_scores.weights = df_scores.weights.fillna(0).add(1)

        # weighted score
        df_scores['final_score'] = df_scores.weights * df_scores.score

        # weighted score by day
        df_scores['day'] = df_scores.index.day
        df_scores['month'] = df_scores.index.month
        df_scores['year'] = df_scores.index.year

        df_scores_daily = df_scores.groupby(['year', 'month', 'day']).sum()
        df_scores_daily.final_score = df_scores_daily.final_score / df_scores_daily.weights
        df_scores_daily['day'] = list(map(lambda x: str(x[2]), df_scores_daily.index))
        df_scores_daily['month'] = list(map(lambda x: str(x[1]), df_scores_daily.index))
        df_scores_daily['year'] = list(map(lambda x: str(x[0]), df_scores_daily.index))
        df_scores_daily.index = pd.to_datetime(df_scores_daily.day + '-'
                                               + df_scores_daily.month + '-'
                                               + df_scores_daily.year)
        df_scores_daily.drop(['year', 'month', 'day'], axis=1, inplace=True)
        return df_scores_daily

    def run(self, df_score: pd.DataFrame, df_level: pd.DataFrame):
        """
        :param df_score: dataframe of scores
        :param df_level: dataframe of levels of the asset
        :return: correlation between score and asset returns
        """
        # get daily scores
        df_scores_returns = self.score_by_day(df_score)

        # get daily returns
        df_scores_returns['returns'] = df_level['Close'].pct_change().shift(-1)

        return self._correlation_method(df_scores_returns.dropna())

    def set_correlation_method(self, correlation_method: str):
        """
        :param correlation_method: method used to compute the correlation
        """
        self._correlation_method = CORRELATION_METHODS[correlation_method]


if __name__ == '__main__':
    from DataAnalysis.sentiment_analysis_light import SentimentAnalysisLight
    from Scrapers.yahoo_scraper import YahooScraper
    from dateutil import relativedelta
    import datetime as dt

    # posts
    posts = pd.read_csv('../Utils/old_reddit_posts.csv', index_col=0).set_index('date')
    posts.index = pd.to_datetime(posts.index)
    posts['title'].fillna('', inplace=True)
    posts['text_content'].fillna('', inplace=True)
    posts['full'] = posts['title'] + ' ' + posts['text_content']
    posts = posts.rename({'score': 'weights'}, axis=1)
    sent_ana = SentimentAnalysisLight()
    posts['score'] = sent_ana.predict(posts['full'])

    # levels
    tickers = ['^NDX']
    scraper = YahooScraper()
    end = dt.datetime.now()
    start = end - relativedelta.relativedelta(months=1)
    levels = scraper.get(tickers, start, end).set_index('Date')

    # correlation
    corr_ana = SentimentReturnCorrelation(correlation_method='sign')
    res = corr_ana.run(posts, levels)
