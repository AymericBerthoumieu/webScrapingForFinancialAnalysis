# Web Scraping for Financial Analysis
Project for the course "Python programming for Finance" at Master 203 at Université Paris Dauphine - PSL

## Introduction
The idea of this project is to check if the sentiment on social networks is correlated with the returns on the markets.
To do so, we load posts from Reddit and Twitter that contains the different tickers that could influence the reference.
For each day, we compute a general sentiment. Then the idea is to compare this sentiment (positive or negative) with the 
return of the reference the next day (because otherwise the posts could react on what already happen and thus 
the correlation could be wrong).

In the next part, one can find **how to launch** and use this software. Then, in the rest of this document one will find
the description of **what each individual file does**.

## How to launch the software ?

 1 - Using a console, go to `./API` and run the file named `api.py`. This program should run in the background all 
 the time.<br>
 2 - Go to `./main.py` and change the variables `ticker_influenced` and `ticker_influencing`.
 3 - Run `./main.py`.

## Description of the files

The description will be done by directory in this project. More details can be found in the description of the methods 
and functions inside the different files.

### Directory : `API`
#### File : `api.py`

This file is responsible of the API. It is where the different end points are implemented and where the api can be 
launched.

#### File : `pipeline.py`

In this file, different pipeline are implemented. Some are here to load the data from webscraping others, more complete,
 implement also the processing of the data.

### Directory : `DataAnalysis`
#### File : `data_cleaner.py`

This file contains the class that cleans the texts loaded. For example, in replace smileys and abbreviations by words.

#### File : `sentiment_analysis.py`

This file contains a class that should do some NLP in order to figure out if a text is positive or negative. But this 
part is not done yet. For now the sentiment analysis is done by `sentiment_analysis_light.py` which is much simple. A 
compromise using the library [text2emotion](https://pypi.org/project/text2emotion/) might be used in the future.

#### File : `sentiment_analysis_light.py`

A simpler method of sentiment analysis is implemented in this file. The idea is just to look if the text contains 
positive or negative words.

#### File : `sentiment_return_correlation.py`

In this file, the class implemented is responsible to compute the sign and pearson correlation of the daily sentiment 
and the returns. <br>
The pearson correlation is define by : <br>
<a href="https://www.codecogs.com/eqnedit.php?latex=\rho&space;=&space;\frac{cov(a,b)}{\sigma_a&space;\sigma_b}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\rho&space;=&space;\frac{cov(a,b)}{\sigma_a&space;\sigma_b}" title="\rho = \frac{cov(a,b)}{\sigma_a \sigma_b}" /></a>
<br>
The sign correlation is define as : <br>
<a href="https://www.codecogs.com/eqnedit.php?latex=\rho&space;=&space;\frac{1}{N}\sum_{i=1}^{N}sign(a_i)&space;\times&space;sign(b_i)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\rho&space;=&space;\frac{1}{N}\sum_{i=1}^{N}sign(a_i)&space;\times&space;sign(b_i)" title="\rho = \frac{1}{N}\sum_{i=1}^{N}sign(a_i) \times sign(b_i)" /></a>
<br>

### Directory : `Scrapers`
#### File : `abbreviation_scraper.py`

This scraper extract abbreviations and their translation.

#### File : `reddit_scraper.py`

This scraper extract post from different subreddits by searching the tickers ordered by "New".

#### File : `scraper.py`

This file contains a mother class (several scrapers inherits from this class) for the scrapers.

#### File : `twitter_scraper.py`

This scraper extract post from Twitter by searching the tickers and ordering by "Most Recent". As this scraper requires 
a connection to a Twitter account, the idea to add it to the pipeline has been given up. Indeed,it would not be easy for
 the user to use it. But the scraper is fully functional.
 
#### File : `yahoo_scraper.py`
 
This scraper load a csv of historical data from Yahoo Finance.
 
### Directory : `Utils`
#### File : `chromedriver.exe`

Necessary file to do web scraping using selenium.

#### File : `const.py`

Contains several constants that are used in the different files of this project.

#### File : `decorators.py`

Only one decorator is implemented yet. It is a timer.

#### File : `exception.py`

Gathers the different exceptions used in this project.
