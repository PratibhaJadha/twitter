import tweepy
from pymongo import MongoClient
from time import sleep
import json

from kafka import KafkaProducer, KafkaConsumer

topic_name = "tweets"
search_words = 'IKEA'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAIz5bQEAAAAA4hCcZ4x%2BPvfn5iMyEiSLyNOWrAA" \
               "%3DQtqkFwK8T97bNLQXjBhOgXaVZRswSoo3ODRBqdncMsaEzuy73T "
access_token_secret = "qiZVl3dVfNLCLcYIAgKX3qV3Y4uzHuruyGQtymtm94BYl"
access_token = "1514632559979868163-nYvfjVESKTF198Z6PTFdm8562k82Q9"
consumer_secret = "xh1JbhvzxBnHLNsXQCEJiyEcXNwm4THcU208ANgfRae8Hyg7xK"
consumer_key = "DtsGUMT6vdEXONSOVfstgY89N"


def Twitter_oauth():
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return client


def get_tweets():
    response = client.search_recent_tweets(query=search_words, tweet_fields=["id", "text", "created_at"])
    return response


def kafka_producer():
    return KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def kafka_consumer():
    return KafkaConsumer(
        'tes',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest'
    )


def produce_tweets_on_kafka(response):
    for tweets in response.data:
        data = {'id': tweets.id, 'text': tweets.text, 'created_at': str(tweets.created_at)}
        kafka_producer().send(topic_name, value=data)
        sleep(1)


def mongo_client():
    client = MongoClient('localhost', 27017)
    db = client['twitter_db']
    return db['twitter_collection']


def store_tweets_to_db():
    for message in kafka_consumer():
        my_json = message.value.decode('utf8')
        data = json.loads(my_json)
        mongo_client().insert_many(data)
    sleep(1)


def tweet_file_to_kafka_to_db():
    tweets_data_path = 'resources/tweets.txt'
    tweets_file = open(tweets_data_path, "r")

    for line in tweets_file:
        tweet = json.loads(line)
        kafka_producer().send(topic_name, value=tweet)
        sleep(1)
    tweets_file.close()


if __name__ == '__main__':
    client = Twitter_oauth()
    tweets = get_tweets()
    produce_tweets_on_kafka(tweets)
    store_tweets_to_db()
    tweet_file_to_kafka_to_db()
