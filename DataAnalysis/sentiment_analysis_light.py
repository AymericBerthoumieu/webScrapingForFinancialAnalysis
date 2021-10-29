from Utils.const import POSITIVE_WORDS, NEGATIVE_WORDS
from Utils.decorators import time_elapsed
import pandas as pd


class SentimentAnalysisLight:

    def __init__(self):
        pass

    @staticmethod
    def sentiment_score(text: str):
        """
        :param text: text to evaluate the sentiment score
        :return: sentiment score of text
        """
        score = 0
        for word in text.split(' '):
            if word in POSITIVE_WORDS:
                score += 1
            elif word in NEGATIVE_WORDS:
                score -= 1
        return score

    @time_elapsed
    def predict(self, s: pd.Series):
        """
        :param s: s of texts (already cleaned) on which sentiment analysis has to be done
        :return: sentiment analysis of the dataframe
        """
        return s.apply(lambda x: self.sentiment_score(x))


if __name__ == '__main__':
    path = "../Utils/old_reddit_posts.csv"
    posts = pd.read_csv(path, index_col=0)

    # sentiment analysis
    sent_ana = SentimentAnalysisLight()
    res = sent_ana.predict(posts['lemmatized_text'])
