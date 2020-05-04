#!/bin/bash
cd /home/ubuntu/apache/kafka_2.12-2.5.0/bin/
echo "Starting Zookeper"
screen -S zookeeper -dm sudo ./zookeeper-server-start.sh /home/ubuntu/apache/kafka_2.12-2.5.0/config/zookeeper.properties
sleep 20s
echo "Zookeper started"
echo ""
echo "Starting Kafka"
screen -S kafka -dm sudo ./kafka-server-start.sh /home/ubuntu/apache/kafka_2.12-2.5.0/config/server.properties
sleep 20s
echo "Kafka started"
echo ""
cd /home/ubuntu/Real-Time-Sentiment-Analysis/
echo "Starting Producer"
screen -S producer -dm python3 tweet_listener.py lockdown
sleep 15s
echo "Producer started"
echo ""
cd /home/ubuntu/elastic/elasticsearch-6.4.2/
echo "Starting Elasticsearch"
screen -S elasticsearch -dm bin/elasticsearch
sleep 15s
echo "Elasticsearch started"
echo ""
echo "Starting Consumer"
screen -S consumer -dm bash -c 'export PYSPARK_PYTHON=python3; cd $SPARK_HOME; sudo bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.0 /home/ubuntu/Real-Time-Sentiment-Analysis/tweet_spark_consumer.py'
sleep 10s
echo "Consumer started"
echo ""
cd /home/ubuntu/elastic/kibana-6.4.2-linux-x86_64/
echo "Starting Kibana"
screen -S kibana -dm bin/kibana
sleep 15s
echo "Kibana started"
