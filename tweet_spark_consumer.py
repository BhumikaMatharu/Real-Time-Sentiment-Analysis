import json

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

import tweet_listener


def sentiment_analysis():
    pass


conf = SparkConf().setMaster("local[*]").setAppName("TwitterStream")
sc = SparkContext()
ssc = StreamingContext(sc, 5)
topic = tweet_listener.brand
kafka_stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {topic: 1})
lines = kafka_stream.map(lambda x: json.loads(x[1]))
#lines.foreachRDD(sentiment_analysis)
lines.pprint()
ssc.start()
ssc.awaitTermination()
