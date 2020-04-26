import json
from kafka import KafkaConsumer

if __name__ == "__main__":
    topic = input("Enter topic: ")
    try:
        consumer = KafkaConsumer( topic,
                         group_id='consumer-group',
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=False,
                         value_deserializer=lambda m: json.loads(m.decode('asciii')),
                         consumer_timeout_ms=1000)
        for tweet in consumer:
            print (tweet.topic, "value:", tweet.value)

    except Exception as ex:
        print("Error")

