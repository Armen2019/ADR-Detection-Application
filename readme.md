# Sentiment Analysis on Tweets with real-time scraping
# The aim of the project was to collect tweets about drugs, predict their positive and negative sentiment.



## Requirements

There are some general library requirements for the project and some which are specific to individual methods. The general requirements are as follows.  
* `numpy`
* `scikit-learn`
* `Scrapy`
* `nltk`
* `langdetect`
* `keras`
* `inflect`
* `flask`

The library requirements specific to some methods are:
* `keras` with `TensorFlow` backend for Logistic Regression, MLP, RNN (LSTM), and CNN.
* `xgboost` for XGBoost.


## Usage

### Running API 

1. Run `app.py ` 

   For testing our API , send request in this format

	  {
    		"start_date": "2018-01-02",    // scraping all tweets from twitter whithin this dates
    		"end_date":   "2018-01-03",    
    		"Tweet":"amlodipine"	     

	  }
		
 The response will be like this (1-for positive tweets, 0-for negative tweets)

   {
      
    {
        "tweet": "Fired my doctor... Dr Neil Levin. Gave me Norvasic  Amlodopine  and a heart monitor.  Amlodopine  causes irregular heartbeat. 
         My ankles became so inflamed and sore I couldn't walk. Quit the drug and ankles returned to normal. Took a month. Couldn't say he was sorry",
        "sentiments": 1
    },
    {
        "tweet": "Amlodipine  may be less likely affected by this - for example it doesn't need to be kept in temperature controlled environment which I wonder if is one of issues here. 
         We certainly need some more info though!!",
        "sentiments": 0
    }
           ---------------------------------
   }
    etc.


## Information about other files

* `Data/tweet`: Real-Time scraped tweets.
* `Data/drug_names`:List of all drug Names.
* `Data/trig-vectors-phrase.bin`: https://data.mendeley.com/datasets/dwr4xn8kcv/3
* `Generator/misspelling_generator.py`: Misspelling generator for every requested tweet. 
* `models/balanced_model.h5`   see sharepoint 