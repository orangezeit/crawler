import requests
from lxml import html
import datetime
import time
from selenium import webdriver


def date_to_timestamp(date):

    return int(datetime.datetime.strptime(date, "%d/%m/%Y").timestamp())


def most_active_tickers(n=100):

    response = requests.get(f'https://finance.yahoo.com/most-active', params={'offset': 0, 'count': n})
    return html.fromstring(response.content).xpath('//td[@aria-label="Symbol"]/a/text()')


def download_requests(tickers, ts1, ts2):

    for ticker in tickers:

        url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}'
        res = requests.get(url, params={'period1': ts1, 'period2': ts2, 'interval': '1d', 'events': 'history'})

        if res.status_code == 200:
            with open(f'{ticker}.csv', 'w') as f:
                # binary data to string
                f.writelines(res.content.decode('utf-8'))
            print('Downloaded')
        else:
            print(res.status_code, 'Download Failed')

        time.sleep(5)


def download_selenium(tickers, ts1, ts2):

    browser = webdriver.Chrome()
    for ticker in tickers:
        browser.get(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}'
                    f'?period1={ts1}&period2={ts2}&interval=1d&events=history')
        time.sleep(5)


if __name__ == '__main__':
    tks = ['BA', 'CSCO', 'DHI', 'DIS', 'JNJ', 'JPM', 'KO', 'MSFT', 'NEE', 'XOM', 'SPY']
    start_ts, end_ts = date_to_timestamp('18/03/2019'), date_to_timestamp('18/03/2020')
    download_requests(tks, start_ts, end_ts)
    download_selenium(tks, start_ts, end_ts)
