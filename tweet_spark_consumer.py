from elastic_search import elastic
from pyspark.sql import *
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
from pyspark.sql.functions import lit
from pyspark.sql.functions import udf
from pyspark.sql.types import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime


def get_sql_context(spark_context):
    if 'sqlContextSingletonInstance' not in globals():
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']


# Perform the sentiment analysis using NLTK Vader
def sentiment_analysis(tweet):
    scores = dict([('pos', 0), ('neu', 0), ('neg', 0), ('compound', 0)])
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(tweet)
    for k in sorted(ss):
        scores[k] += ss[k]

    return json.dumps(scores)

# The function called for each RDD
def analyze(time, rdd):
    print("========= %s =========" % str(time))
    try:
        if rdd.count() == 0:
            raise Exception('Empty')

        sql_context = get_sql_context(rdd.context)
        df = sql_context.read.json(rdd)
        df = df.filter("text not like 'RT %'")
        if df.count() == 0:
            raise Exception('Empty')

        # Call the sentiment_analysis() function for every tweet
        # Add the result to the data as column "sentiment"
        analysis = udf(lambda x: sentiment_analysis(x), returnType=StringType())
        df = df.withColumn("sentiment", lit(analysis(df.text)))
        print(df.take(10))
        results = df.toJSON().map(lambda j: json.loads(j)).collect()

        for result in results:
            result["date"] = datetime.strptime(result["date"], "%Y-%m-%d %H:%M:%S")
            result["sentiment"] = json.loads(result["sentiment"])

        elastic(results, "lockdown", "doc")

    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    # Create a SparkContext with the appName and set the logging level
    sc = SparkContext(appName="PythonStreaming")
    sc.setLogLevel("ERROR")

    # Create a Streaming Context which waits for 3 seconds to consume the next package of tweets
    ssc = StreamingContext(sc, 3)

    # Initialize a Kafka Consumer Stream
    kafka_stream = KafkaUtils.createStream(ssc, "localhost:2181", "consumer-group", {"lockdown": 1})

    # For each RDD in the steam call analyze()
    lines = kafka_stream.map(lambda x: json.loads(x[1]))
    lines.foreachRDD(analyze)

    # Start the Spark Streaming job
    ssc.start()
    ssc.awaitTermination()
