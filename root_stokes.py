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
# URL of the Cricinfo for Root ODI page
url = "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=2;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings"

# Add a custom User-Agent header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Make the GET request with headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table with the innings data (Table 4 in your case)
    innings_table = soup.find_all("table", class_="engineTable")[3]  # Fourth table
    
    # Get the first date in the list
    latest_date = innings_table.find_all("tr", class_="data1")[0].find_all("td")[-2].get_text(strip=True)  # Data rows)
      
    
    if latest_date:
        # Convert the string dates into datetime objects for sorting

        date_format = "%d %b %Y"  # The format in which the date appears (e.g., "23 Jun 2022")
        
        # Convert each date string into a datetime object
        latest_start_date = datetime.strptime(latest_date, date_format) 
    
        # print(latest_start_date)
        
        # Print the latest start date in the desired format
        print(f"Latest Start Date: {latest_start_date.strftime('%d %b %Y')}")
    else:
        print("No start dates found.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")



# Starting number and the date tracking the first tweet
root_last_test_century = date(2024, 12, 8)
root_last_ODI_century = latest_start_date.date()
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
