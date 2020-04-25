from datetime import datetime, timezone
import tweepy
import json
from kafka import KafkaProducer
import credentials
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


class TweetListener(tweepy.StreamListener):
    def __init__(self, brand_name):
        super().__init__()
        self.producer = KafkaProducer(bootstrap_servers="localhost:9092", api_version=(0, 10, 1),
                                      value_serializer=lambda m: json.dumps(m).encode('ascii'))
        self.brand_name = brand_name

    def clean_tweet(self, raw_data):
        json_data = json.loads(raw_data)
        tweet = dict()

        tweet["date"] = datetime.strptime(json_data["created_at"], '%a %b %d %H:%M:%S %z %Y') \
            .replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')

        tweet["user"] = json_data["user"]["screen_name"]

        if "extended_tweet" in json_data:
            tweet["text"] = json_data["extended_tweet"]["full_text"]
        else:
            tweet["text"] = json_data["text"]

        return json.dumps(tweet)

    def on_data(self, raw_data):
        clean_data = self.clean_tweet(raw_data)
        self.producer.send(self.brand_name.replace("#", ""), clean_data)
        print(clean_data)

    def on_error(self, status_code):
        print(status_code)
        return True

    def on_timeout(self):
        return True


def start_twitter_stream():
    listener = TweetListener(brand_name)
    auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream = tweepy.Stream(auth, listener, tweet_mode="extended")
    stream.filter(track=[brand_name], languages=["en"])


def process():
    pass


def start_spark_streaming():
    sc = SparkContext(appName="TwitterStreaming")
    ssc = StreamingContext(sc, 3)
    kafka_stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {brand_name: 1})
    lines = kafka_stream.map(lambda x: json.loads(x[1]))
    lines.foreachRDD(process)
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    brand_name = input("Enter a hashtag: ")
    start_twitter_stream()
    start_spark_streaming()
