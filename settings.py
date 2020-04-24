TRACK_WORDS = ["coronavirus"]
TABLE_NAME = "coronavirus"
TABLE_ATTRIBUTES = "id_str VARCHAR(255), created_at DATETIME, text VARCHAR(255), \
            polarity INT, subjectivity INT, user_location VARCHAR(255), \
            user_description VARCHAR(255), longitude DOUBLE, latitude DOUBLE, \
            retweet_count INT, favorite_count INT"