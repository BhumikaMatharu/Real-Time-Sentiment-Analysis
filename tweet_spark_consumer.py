import json

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

from kafka import KafkaConsumer

import tweet_listener


def sentiment_analysis():
    pass


if __name__ == "main":
    consumer = KafkaConsumer(tweet_listener.brand,
                                     group_id='consumer-group',
                                     bootstrap_servers=['localhost:9092'],
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=False,
                                     value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                     consumer_timeout_ms=1000)

    conf = SparkConf().setMaster("local[*]").setAppName("TwitterStream")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 5)
    topic = tweet_listener.brand
    kafka_stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {topic: 1})
    lines = kafka_stream.map(lambda x: json.loads(x[1]))
    lines.pprint()
    ssc.start()
    ssc.awaitTermination()
