from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from DataAnalysis.data_cleaner import DataCleaner
from sklearn.naive_bayes import GaussianNB
from Utils.decorators import time_elapsed
from nltk.corpus import twitter_samples
import pandas as pd
import numpy as np
import joblib
import nltk


class SentimentAnalysis:
    """
    Source : https://medium.com/geekculture/a-tutorial-on-performing-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk-40e5b35ab440
    """

    def __init__(self):
        self.count_vect = CountVectorizer(max_features=1000, min_df=1, max_df=1.0)
        self.model = self.get_model()

    @time_elapsed
    def get_model(self):
        nltk.download("twitter_samples")
        # Datasets to train the model
        positive_tweets = twitter_samples.strings('positive_tweets.json')
        negative_tweets = twitter_samples.strings('negative_tweets.json')
        # Create a dataframe from positive tweets
        df = pd.DataFrame(positive_tweets, columns=['Tweet'])
        # Add a column to dataframe for positive sentiment value 1
        df['Sentiment'] = 1
        # Create a temporary dataframe for negative tweets
        temp_df = pd.DataFrame(negative_tweets, columns=['Tweet'])
        # Add a column to temporary dataframe for negative sentiment value 0
        temp_df['Sentiment'] = 0
        # Combine positive and negative tweets in one single dataframe
        df = df.append(temp_df, ignore_index=True)
        df = df.sample(frac=1)
        df.reset_index(drop=True, inplace=True)

        cleaner = DataCleaner()
        df['lemmatized_text'] = df['Tweet'].apply(lambda x: cleaner.run(x))

        # self.count_vect = self.count_vect.fit(df['lemmatized_text'])
        # joblib.dump(self.count_vect, '../Utils/countvect.pkl')
        self.count_vect.fit(df['lemmatized_text'])
        matrix_features = self.get_features(df)

        X_train, X_test, y_train, y_test = train_test_split(matrix_features.toarray(),
                                                            df['Sentiment'],
                                                            test_size=0.01,
                                                            random_state=42)
        nb_clf = GaussianNB()
        nb_clf.fit(X_train, y_train)
        return nb_clf

    def get_features(self, df: pd.DataFrame):
        """
        :param df: dataframe from which features have to be extracted
        :return: features of text
        """

        # To get a sparse matrix of the words in the text
        matrix_features = self.count_vect.transform(df["lemmatized_text"])
        return matrix_features

    @time_elapsed
    def predict(self, df: pd.DataFrame):
        """
        :param df: dataframe (already cleaned) on which sentiment analysis has to be done
        :return: sentiment analysis of the dataframe
        """
        matrix_features = self.get_features(df)
        prediction = self.model.predict(matrix_features.toarray())
        return prediction


if __name__ == '__main__':
    # from DataAnalysis.data_cleaner import DataCleaner
    # from Scrapers.reddit_scraper import RedditScraper
    # from dateutil import relativedelta
    # import datetime as dt
    #
    # # data
    # subreddit = "wallstreetbets"
    # tickers = ['AAPL']
    # end_date = dt.datetime.now()
    # start_date = end_date - relativedelta.relativedelta(years=1)
    # scraper = RedditScraper(subreddit)
    # posts = scraper.get(tickers, start_date, end_date)
    # posts['full'] = posts['title'] + ' ' + posts['text_content']
    #
    # # cleaning
    path = "../Utils/old_reddit_posts.csv"
    # cleaner = DataCleaner()
    # posts['lemmatized_text'] = posts['full'].apply(lambda x: cleaner.run(x))
    # posts.to_csv(path)
    posts = pd.read_csv(path, index_col=0)

    # sentiment analysis
    sent_ana = SentimentAnalysis()
    res = sent_ana.predict(posts)
