cd C:\Apache\kafka_2.12-2.5.0\bin\windows
START "" zookeeper-server-start.bat C:\Apache\kafka_2.12-2.5.0\config\zookeeper.properties
timeout 15
START "" kafka-server-start.bat C:\Apache\kafka_2.12-2.5.0\config\server.properties
timeout 20
cd C:\Users\prath\PycharmProjects\Real-Time-Sentiment-Analysis
START "" python tweet_listener.py
timeout 15
START "" C:\Elastic\elasticsearch-7.6.2\bin\elasticsearch
timeout 15
START "" %SPARK_HOME%\bin\spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.0 C:\Users\prath\PycharmProjects\Real-Time-Sentiment-Analysis\tweet_spark_consumer.py
PAUSE