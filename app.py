from flask import Flask, jsonify
from flask import request
import pandas as pd

from ScrapingUtils import ScrapingUtils
from SentimentAnalyzer import SentimentAnalyze

app = Flask(__name__)


@app.route('/sentiments', methods=['POST', 'GET'])
def adr_in_tweets():
    content = request.get_json()
    if content['start_date'] > content['end_date']:
        return jsonify({"Start date must be greater"})
    else:
        scraping = ScrapingUtils()
        scraping.search_tweet(content['Tweet'], content['start_date'], content['end_date'])
        sentiments = SentimentAnalyze().sentiment()
        scraping.tweets_sentiment_vector(sentiments)
        df = pd.read_excel('Data/output.xlsx')
        result = df.to_json(orient="records")
        return result


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=False)
