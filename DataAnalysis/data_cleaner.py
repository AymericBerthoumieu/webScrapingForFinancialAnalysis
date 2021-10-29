from Scrapers.abbreviations_scraper import AbbreviationsScraper
from Utils.const import DICT_SMILEY, WORDS_TO_KEEP
from Utils.decorators import time_elapsed
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections.abc import Iterable
import string
import nltk
import re


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


class DataCleaner:

    def __init__(self):
        self.abbreviation_translator = AbbreviationsScraper(begin=2, end=26, lower=True).get().set_index('abbreviation')
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = stopwords.words('english')
        for w in WORDS_TO_KEEP:
            self.stop_words.remove(w)

    @staticmethod
    def to_lowercase(text: str):
        """
        :param text: text to clean
        :return: same text only with lower case
        """
        return text.lower()

    @staticmethod
    def remove_urls(text: str):
        """
        :param text: text to clean
        :return: url removed from text
        """
        text = re.sub('http[s]?://(?:[a-zA-Z]|[0–9]|[$-_@.&+#]|[!*\(\),]|(?:%[0–9a-fA-F][0–9a-fA-F]))+', '', text)
        return text

    @staticmethod
    def words_translation(words: list, translator: dict, avoid: Iterable = ()):
        """
        :param words: list of words
        :param translator: mapper from one form of a word to another
        :param avoid: abbreviation that should not be translated
        :return: words with translation done
        """
        for i in range(len(words)):
            if words[i] not in avoid and translator.get(words[i]):
                words[i] = translator[words[i]]
        return words

    def remove_abbreviations(self, text: str, avoid: Iterable = ()):
        """
        :param text: text to clean
        :param avoid: abbreviation that should not be translated
        :return: abbreviation replaced by full words
        """
        words = text.split(" ")
        translation = self.abbreviation_translator
        return " ".join(DataCleaner.words_translation(words, translation.to_dict()['explanation'], avoid))

    @staticmethod
    def remove_smiley(text: str):
        """
        :param text: text to clean
        :return: smiley replaced by words
        """
        words = text.split(" ")
        return " ".join(DataCleaner.words_translation(words, DICT_SMILEY))

    @staticmethod
    def remove_noise(text: str):
        """
        :param text: text to clean
        :return: removing twitter handles, punctuation, extra spaces, numbers and special characters
        """
        text = re.sub("(@[A-Za-z0–9_]+)", "", text)
        text = "".join([char if char not in string.punctuation else " " for char in text])
        text = re.sub(" +", " ", text)
        text = re.sub("[0–9]+", "", text).split(" ")
        for i in range(len(text)):
            text[i] = re.sub("[^A-Za-z0–9_.]", "", text[i])
        return " ".join(text)

    def remove_stop_words(self, text: str):
        """
        :param text: text to clean
        :return: remove stop words
        """
        tokens = word_tokenize(text)
        text_with_no_stop_words = [token for token in tokens if token not in self.stop_words]
        reformed_text = " ".join(text_with_no_stop_words)
        return reformed_text

    @staticmethod
    def get_wordnet_pos(word):
        """
        :param word: word to work on
        :return: Map POS tag to first character lemmatize() accepts
        """
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)

    def lemmatize_sentence(self, sentence: str):
        """
        :param sentence: sentence that has to be lemmatize
        :return:
        """
        token_words = word_tokenize(sentence)
        lemmatized_sentence = []
        for word in token_words:
            lemmatized_sentence.append(self.lemmatizer.lemmatize(word, self.get_wordnet_pos(word)))
        lemmatized_sentence.append(" ")

        return "".join(lemmatized_sentence)

    def run(self, text: str, avoid: Iterable = ()):
        """
        :param text: text to clean
        :param avoid: abbreviations that have not to be translated
        :return: text cleaned
        """
        text = self.to_lowercase(text)
        text = self.remove_urls(text)
        text = self.remove_abbreviations(text, avoid)
        text = self.remove_smiley(text)
        text = self.remove_noise(text)
        text = self.remove_stop_words(text)
        text = self.lemmatize_sentence(text)

        return text


if __name__ == '__main__':
    cleaner = DataCleaner()
    res = cleaner.run('gg mate, btw sell ;) <3')
