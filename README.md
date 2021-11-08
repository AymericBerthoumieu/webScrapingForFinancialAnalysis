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
and the returns.
The pearson correlation is define by : $\rho = \frac{cov(a,b)}{\sigma_a \sigma_b}$

