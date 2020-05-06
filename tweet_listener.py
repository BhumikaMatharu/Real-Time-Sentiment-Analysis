import string
from datetime import datetime, timezone
import tweepy
import json
from kafka import KafkaProducer
import credentials
import sys
import preprocessor as p

brand = str


class TweetListener(tweepy.StreamListener):
    def __init__(self, brand_name):
        super().__init__()
        self.brand_name = brand_name

    # Utility function to remove emojis
    def remove_emojis(self, text):
        if text:
            return text.encode("ascii", "ignore").decode("ascii")
        else:
            return None

    # Utility function to clean the tweets
    def clean_tweet(self, raw_data):
        try:
            json_data = json.loads(raw_data)
            # print(json_data["coordinates"])
            tweet = dict()
            tweet["date"] = datetime.strptime(json_data["created_at"], '%a %b %d %H:%M:%S %z %Y') \
                .astimezone(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            tweet["user"] = json_data["user"]["screen_name"]

            if "extended_tweet" in json_data:
                #tweet["text"] = self.remove_emojis(json_data["extended_tweet"]["full_text"])\
                    #.translate(str.maketrans('', '', string.punctuation)).replace("\n", " ")
                tweet["text"] = p.clean(json_data["extended_tweet"]["full_text"])
            else:
                #tweet["text"] = self.remove_emojis(json_data["text"])\
                    #.translate(str.maketrans('', '', string.punctuation)).replace("\n", " ")
                tweet["text"] = p.clean(json_data["text"])

            if json_data["coordinates"] is not None:
                print(json_data["coordinates"])
                longitude = json_data["coordinates"]["coordinates"][0]
                latitude = json_data["coordinates"]["coordinates"][1]
                tweet["location"] = str(latitude) + "," + str(longitude)

            return json.dumps(tweet)

        except Exception as e:
            return True

    # Defines the behaviour on receiving data
    def on_data(self, raw_data):
        try:
            clean_data = self.clean_tweet(raw_data)
            producer.send(self.brand_name.replace("#", ""), clean_data)
            print(clean_data)
        except Exception as e:
            return True

    # Defines the behaviour on error
    def on_error(self, status_code):
        print(status_code)
        return True

    # Defines the behaviour on timeout
    def on_timeout(self):
        return True


if __name__ == "__main__":
    # Get the brand to be tracked from the user
    brand = sys.argv[1]

    # Initialize a Kafka Producer
    producer = KafkaProducer(bootstrap_servers="localhost:9092", api_version=(0, 10, 1),
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))

    listener = TweetListener(brand)

    # Start the Twitter stream
    auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    stream = tweepy.Stream(auth, listener, tweet_mode="extended")
    # stream.filter(track=[brand], languages=["en"])
    stream.filter(locations=[-180,-90,180,90], languages=["en"])
