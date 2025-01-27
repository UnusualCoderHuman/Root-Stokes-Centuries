import tweepy
import os
from datetime import date, datetime

# Fetch Twitter API credentials from environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
# Authenticate with the Twitter API
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Starting number and the date tracking the first tweet
root_last_test_century = date(2024, 12, 8)
root_last_ODI_century = date(2019,6,14)
stokes_last_century = date(2023,11,8)
stokes_last_test_century= date(2023,7,2)
stokes_last_test_century_in_winning_cause = date(2022,8,26)

def daily_tweet():
    today = date.today()
    
    # Calculate the number of days since each milestone
    days_elapsed_since_root_last_test_century = (today - root_last_test_century).days
    days_elapsed_since_root_last_ODI_century = (today - root_last_ODI_century).days
    days_elapsed_since_stokes_last_century = (today - stokes_last_century).days
    days_elapsed_since_stokes_last_test_century = (today - stokes_last_test_century).days
    days_elapsed_since_stokes_last_test_century_in_winning_cause = (today - stokes_last_test_century_in_winning_cause).days

    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        # Post the tweet
        tweet_text = (
            f"{days_elapsed_since_root_last_test_century} days since Joe Root's last Test century.\n"
            f"{days_elapsed_since_root_last_ODI_century} days since Joe Root's last ODI century.\n"
            f"{days_elapsed_since_stokes_last_century} days since Ben Stokes' last century.\n"
            f"{days_elapsed_since_stokes_last_test_century} days since Ben Stokes' last Test century.\n"
            f"{days_elapsed_since_stokes_last_test_century_in_winning_cause} days since Ben Stokes' last Test century in a winning cause.\n"
            f"This was tweeted at {timestamp}"
        )
        
        client.create_tweet(text=tweet_text)
        print(f"Tweeted successfully!")

    except Exception as e:
        print(f"Error while tweeting: {e}")


    
if __name__ == "__main__":
    try:
        user = client.get_me()
        print(f"Authenticated as: {user.data['username']}")
        daily_tweet()
    except Exception as e:
         print(f"Error: {e}")
