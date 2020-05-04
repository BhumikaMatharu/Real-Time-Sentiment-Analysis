#!/bin/bash
cd /home/ubuntu/apache/kafka_2.12-2.5.0/bin/
screen -S zookeeper -dm sudo ./zookeeper-server-start.sh /home/ubuntu/apache/kafka_2.12-2.5.0/config/zookeeper.properties
screen -S kafka -dm sudo ./kafka-server-start.sh /home/ubuntu/apache/kafka_2.12-2.5.0/config/server.properties
export SPARK_HOME='/home/ubuntu/apache/spark-2.2.2-bin-hadoop2.7/'
export PYSPARK_PYTHON=python3
cd $SPARK_HOME
screen -S kafka -dm sudo bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.0 /home/ubuntu/Real-Time-Sentiment-Analysis/tweet_spark_consumer.py
cd /home/ubuntu/elastic/elasticsearch-6.4.2/
screen -S elasticsearch -dm bin/elasticsearch
cd /home/ubuntu/elastic/kibana-6.4.2-linux-x86_64/
screen -S kibana -dm bin/kibana
