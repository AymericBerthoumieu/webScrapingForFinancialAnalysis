import requests
import ast

# ticker of the index
ticker_influenced = '^NDX'

# tickers of stocks that can influence the index
ticker_influencing = ['AAPL', 'FB']  #, 'META', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'NVDA', 'NFLX']


# url of request
url = "http://127.0.0.1:5000/correlation_live?ticker={}&influencers={}"


# request data
response = requests.get(url.format(ticker_influenced, ",".join(ticker_influencing)))

if response.status_code == 200:
    res = ast.literal_eval(response.text.replace("\n", ""))
    corr_sign = res["sign_correlation"]
    corr_pearson = res["pearson_correlation"]
    print(f"Sign correlation : {corr_sign} \nPearson correlation : {corr_pearson}")
