from Utils.decorators import time_elapsed
from lxml import html
import pandas as pd
import requests


class AbbreviationsScraper:
    _URL = "https://en.wiktionary.org/wiki/Appendix:English_internet_slang"

    def __init__(self, begin: int = 0, end: int = 27, lower: bool = False):
        self.begin = begin
        self.end = end
        self.lower = lower

    @time_elapsed
    def get(self):
        page = requests.get(self._URL)
        tree = html.fromstring(page.content, 'lxml')

        accumulator = list()
        for i in range(self.begin, self.end):
            ul = tree.xpath(f'//*[@id="mw-content-text"]/div[1]/ul[{i}]')[0]
            for abbrev in ul:
                short, long = map(lambda x: x.strip().lower(), abbrev.text_content().split(':')[:2])
                accumulator.append({
                    "abbreviation": short,
                    "explanation": long.split(',')[0].split('.')[0].split(";")[0],
                })
        return pd.DataFrame(accumulator)


if __name__ == '__main__':
    scraper = AbbreviationsScraper(2, 26, True)
    res = scraper.get()
