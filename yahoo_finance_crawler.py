import requests
from lxml import html
import datetime
import time


def most_active_tickers(n=100):

    response = requests.get(f'https://finance.yahoo.com/most-active', params={'offset': 0, 'count': n})
    return html.fromstring(response.content).xpath('//td[@aria-label="Symbol"]/a/text()')


def download(tickers, ts1, ts2):

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

    params = {'period1': ts1, 'period2': ts2, 'interval': '1d', 'events': 'history', 'crumb': 'EMffa389yEV'}

    cookie = {'cookie': 'ucs=lnct=1541772976; GUC=AQEBAQFcgzBdT0IjTgTp&s=AQAAAAfxxG2R&g=XIHtIA; '
                        'APID=VBb725f994-6d24-11e8-b01a-0693a59ac389; B="bfichthd7p4fk&b=3&s=mt"; '
                        'thamba=1; PRF=t%3DAAPL%252B000016.SS%252BDIS%252B601398.SS%252BSPY%252BXOM%252BNEE'
                        '%252BMSFT%252BKO%252BJPM%252BJNJ%252BDHI%252BCSCO%252BBA%252BGOOG%26qct%3Dcandle'
                        '%26ext-feedback%3D1; cmp=t=1565182548&j=0'}

    for ticker in tickers:

        url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}'
        res = requests.get(url, params=params, headers=headers, cookies=cookie)

        if res.status_code == 200:
            with open(f'{ticker}.csv', 'w') as f:
                # binary data to string
                f.writelines(res.content.decode('utf-8'))
            print('Downloaded')
        else:
            print(res.status_code, 'Download Failed')
        time.sleep(5)


if __name__ == '__main__':
    # tks = ['BA', 'CSCO', 'DHI', 'DIS', 'JNJ', 'JPM', 'KO', 'MSFT', 'NEE', 'XOM', 'SPY']
    # tks = ['601398.SS', '600028.SS', '600019.SS', '600018.SS', '600050.SS',
    #        '600519.SS', '000063.SZ', '002024.SZ', '000839.SZ', '600177.SS']

    tks = ['BA', 'CSCO']
    start_ts = datetime.datetime.strptime('01/01/1998', "%d/%m/%Y").timestamp()
    end_ts = datetime.datetime.strptime('31/12/2001', "%d/%m/%Y").timestamp()
    # download(tks, int(start_ts), int(end_ts))
    most_active_tickers()
