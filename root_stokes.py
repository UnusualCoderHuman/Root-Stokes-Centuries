import tweepy
import os
from datetime import date, datetime

# Twitter API setup from environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Dates of last century
milestone_dates = {
    "root_test": date(2026, 1, 5),
    "root_odi": date(2026, 1, 27),
}

# Tweet
def daily_tweet():
    today = date.today()
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Build Root block
    root_block = [
        ((today - milestone_dates['root_test']).days, "Joe Root's last Test century"),
        ((today - milestone_dates['root_odi']).days, "Joe Root's last ODI century")
    ]
    root_block.sort(key=lambda x: x[0])  # sort by days
    
    # Create tweet
    tweet_text = (
        "\n".join([f"{days} days since {desc}." for days, desc in root_block]) + "\n" +
        "\n".join([f"{days} days since {desc}." for days, desc in stokes_block]) + "\n" +
        f"This was tweeted at {timestamp}"
    )
    
    try:
        client.create_tweet(text=tweet_text)
        print("✅ Tweet posted successfully!")
    except Exception as e:
        print(f"❌ Error while tweeting: {e}")

# -------------------- Run --------------------

if __name__ == "__main__":
    try:
        user = client.get_me()
        print(f"Authenticated as: {user.data['username']}")
        daily_tweet()
    except Exception as e:
        print(f"❌ Error: {e}")
