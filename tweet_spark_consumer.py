import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

import tweet_listener


def sentiment_analysis():
    pass


if __name__ == "main":
    sc = SparkContext(appName="SentimentAnalysis")
    ssc = StreamingContext(sc, 5)
    topic = tweet_listener.brand
    kafka_stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {topic: 1})
    parsed = kafka_stream.map(lambda v: json.loads(v[1]))
    user_counts = parsed.map(lambda tweet: (tweet['user']["screen_name"], 1)).reduceByKey(lambda x, y: x + y)
    user_counts.pprint()
    ssc.start()
    ssc.awaitTermination()
