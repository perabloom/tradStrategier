import datetime

from polygon import RESTClient
import sys

def ts_to_datetime(ts) -> str:
    return datetime.datetime.fromtimestamp(ts / 1000.0).strftime('%Y-%m-%d %H:%M')


def getNews(symbol, count = 2):
    key = "K4i_pO9R1pcyv4ule1lnka3owpJ7T2b8"

    # RESTClient can be used as a context manager to facilitate closing the underlying http session
    # https://requests.readthedocs.io/en/master/user/advanced/#session-objects
    with RESTClient(key) as client:
        resp = client.reference_ticker_news_v2(ticker=symbol)
        results = resp.results
        for news in results:
            print(news)
            print("**** ", news['published_utc'], news['article_url'])
            print("\n")
            count -= 1
            if (count == 0):
                break


if __name__ == '__main__':
    getNews(sys.argv[1], int(sys.argv[2]))
