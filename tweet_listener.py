from datetime import datetime, timezone
import tweepy
import json
from kafka import KafkaProducer
import credentials


class TweetListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        self.producer = KafkaProducer(bootstrap_servers="localhost:9092", api_version=(0, 10, 1),
                                      value_serializer=lambda m: json.dumps(m).encode('ascii'))

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
        self.producer.send("coronavirus", clean_data)
        print(clean_data)

    def on_error(self, status_code):
        print(status_code)


if __name__ == "__main__":
    listener = TweetListener()
    auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream = tweepy.Stream(auth, listener, tweet_mode="extended")
    stream.filter(track=["#coronavirus"], languages=["en"])