import tweepy
from textblob import TextBlob
import credentials
import settings
import mysql.connector


# A listener class for listening to tweets
class Listener(tweepy.StreamListener):
    # Remove the non-ASCII characters (emojis)
    def remove_emojis(self, text):
        if text:
            return text.encode("ascii", "ignore").decode("ascii")
        else:
            return None

    # Extract the information from tweets
    def on_status(self, status):
        id_str = status.id_str
        created_at = status.created_at
        text = self.remove_emojis(status.text)
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity

        user_location = self.remove_emojis(status.user.location)
        user_description = self.remove_emojis(status.user.description)
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]

        retweet_count = status.retweet_count
        favorite_count = status.favorite_count

        print(status.text)
        print("Longitude: {}, Latitude: {}".format(longitude, latitude))

        if my_db.is_connected():
            my_cursor = my_db.cursor()
            sql = "INSERT INTO {} (id_str, created_at, text, polarity, subjectivity, user_location, \
            user_description, longitude, latitude, retweet_count, favorite_count) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
                .format(settings.TABLE_NAME)
            val = (id_str, created_at, text, polarity, subjectivity, user_location,
                   user_description, longitude, latitude, retweet_count, favorite_count)
            my_cursor.execute(sql, val)
            my_db.commit()
            my_cursor.close()

    # Stop scraping if the rate exceeds the maximum limit
    def on_error(self, status_code):
        if status_code == 420:
            return False


# Create and connect with a MySQL database for storage
my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="CS267",
    database="TwitterDB",
    charset="utf8"
)

# Create a new table if it does not already exist
if my_db.is_connected():
    my_cursor = my_db.cursor()
    my_cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(settings.TABLE_NAME))
    if my_cursor.fetchone()[0] != 1:
        my_cursor.execute("CREATE TABLE {} ({})"
                          .format(settings.TABLE_NAME, settings.TABLE_ATTRIBUTES))
        my_db.commit()
    my_cursor.close()

# Authenticate the application and registering it with Twitter
auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Start the listener with Oauth
tweet_listener = Listener()
my_stream = tweepy.Stream(auth=api.auth, listener=tweet_listener)
my_stream.filter(languages=["en"], track=settings.TRACK_WORDS)
