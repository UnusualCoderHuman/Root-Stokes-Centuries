import tweepy
import os
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup

# Twitter API setup
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

# --- Function to read last known date from file ---
def load_last_recorded_date(filename):
    try:
        with open(filename, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

# --- Function to write the newly discovered date ---
def update_recorded_date(filename, new_date):
    with open(filename, "w") as f:
        f.write(new_date.strftime("%Y-%m-%d"))

# --- Function to fetch latest match start date from a Cricinfo URL ---
def fetch_latest_start_date(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    try:
        innings_table = soup.find_all("table", class_="engineTable")[3]
        latest_date_str = innings_table.find_all("tr", class_="data1")[0].find_all("td")[-2].get_text(strip=True)
        return datetime.strptime(latest_date_str, "%d %b %Y").date()
    except Exception as e:
        print(f"Error parsing start date from {url}: {e}")
        return None

# --- Cricinfo URLs ---
urls = {
    "root_odi": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=2;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "root_test": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_test": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_all": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=11;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_winning": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;result=1;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings"
}

# --- File mappings for date tracking ---
date_files = {
    "root_odi": "root_odi.txt",
    "root_test": "root_test.txt",
    "stokes_test": "stokes_test.txt",
    "stokes_all": "stokes_all.txt",
    "stokes_winning": "stokes_winning.txt"
}

# --- Default (hardcoded) milestone dates ---
root_last_test_century = date(2024, 12, 8)
root_last_ODI_century = date(2025, 6, 1)
stokes_last_test_century = date(2023, 7, 2)
stokes_last_century = date(2023, 11, 8)
stokes_last_winning_cause = date(2022, 8, 26)

# --- Update logic ---
milestone_dates = {
    "root_odi": root_last_ODI_century,
    "root_test": root_last_test_century,
    "stokes_test": stokes_last_test_century,
    "stokes_all": stokes_last_century,
    "stokes_winning": stokes_last_winning_cause
}

for key in urls:
    latest_start_date = fetch_latest_start_date(urls[key])
    if not latest_start_date:
        continue

    last_recorded_date = load_last_recorded_date(date_files[key])

    # If no file exists or new date found
    if last_recorded_date is None or latest_start_date != last_recorded_date:
        print(f"[{key}] New update detected. Using today's date: {date.today().strftime('%d %b %Y')}")
        milestone_dates[key] = date.today()
        update_recorded_date(date_files[key], latest_start_date)
    else:
        milestone_dates[key] = last_recorded_date

# --- Prepare tweet ---
def daily_tweet():
    today = date.today()
    timestamp = datetime.now().strftime("%H:%M:%S")

    tweet_text = (
        f"{(today - milestone_dates['root_test']).days} days since Joe Root's last Test century.\n"
        f"{(today - milestone_dates['root_odi']).days} days since Joe Root's last ODI century.\n"
        f"{(today - milestone_dates['stokes_all']).days} days since Ben Stokes' last century.\n"
        f"{(today - milestone_dates['stokes_test']).days} days since Ben Stokes' last Test century.\n"
        f"{(today - milestone_dates['stokes_winning']).days} days since Ben Stokes' last Test century in a winning cause.\n"
        f"This was tweeted at {timestamp}"
    )

    try:
        client.create_tweet(text=tweet_text)
        print("Tweeted successfully!")
    except Exception as e:
        print(f"Error while tweeting: {e}")

# --- Run ---
if __name__ == "__main__":
    try:
        user = client.get_me()
        print(f"Authenticated as: {user.data['username']}")
        daily_tweet()
    except Exception as e:
        print(f"Error: {e}")

# import tweepy
# import os
# from datetime import date, datetime
# import requests
# from bs4 import BeautifulSoup

# # Fetch Twitter API credentials from environment variables
# API_KEY = os.getenv('API_KEY')
# API_SECRET_KEY = os.getenv('API_SECRET_KEY')
# ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
# ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
# BEARER_TOKEN = os.getenv('BEARER_TOKEN')
# # Authenticate with the Twitter API
# client = tweepy.Client(
#     bearer_token=BEARER_TOKEN,
#     consumer_key=API_KEY,
#     consumer_secret=API_SECRET_KEY,
#     access_token=ACCESS_TOKEN,
#     access_token_secret=ACCESS_TOKEN_SECRET
# )
# # URL of the Cricinfo for Root ODI page
# url = "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=2;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings"

# # Add a custom User-Agent header
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }

# # Make the GET request with headers
# response = requests.get(url, headers=headers)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(response.content, "html.parser")
    
#     # Find the table with the innings data (Table 4 in your case)
#     innings_table = soup.find_all("table", class_="engineTable")[3]  # Fourth table
    
#     # Get the first date in the list
#     latest_date = innings_table.find_all("tr", class_="data1")[0].find_all("td")[-2].get_text(strip=True)  # Data rows)
      
    
#     if latest_date:
#         # Convert the string dates into datetime objects for sorting

#         date_format = "%d %b %Y"  # The format in which the date appears (e.g., "23 Jun 2022")
        
#         # Convert each date string into a datetime object
#         latest_start_date = datetime.strptime(latest_date, date_format) 
    
#         # print(latest_start_date)
        
#         # Print the latest start date in the desired format
#         print(f"Latest Start Date: {latest_start_date.strftime('%d %b %Y')}")
#     else:
#         print("No start dates found.")
# else:
#     print(f"Failed to fetch the page. Status code: {response.status_code}")



# # Starting number and the date tracking the first tweet
# root_last_test_century = date(2024, 12, 8)
# root_last_ODI_century = latest_start_date.date()
# stokes_last_century = date(2023,11,8)
# stokes_last_test_century= date(2023,7,2)
# stokes_last_test_century_in_winning_cause = date(2022,8,26)

# def daily_tweet():
#     today = date.today()
    
#     # Calculate the number of days since each milestone
#     days_elapsed_since_root_last_test_century = (today - root_last_test_century).days
#     days_elapsed_since_root_last_ODI_century = (today - root_last_ODI_century).days
#     days_elapsed_since_stokes_last_century = (today - stokes_last_century).days
#     days_elapsed_since_stokes_last_test_century = (today - stokes_last_test_century).days
#     days_elapsed_since_stokes_last_test_century_in_winning_cause = (today - stokes_last_test_century_in_winning_cause).days

#     timestamp = datetime.now().strftime("%H:%M:%S")

#     try:
#         # Post the tweet
#         tweet_text = (
#             f"{days_elapsed_since_root_last_test_century} days since Joe Root's last Test century.\n"
#             f"{days_elapsed_since_root_last_ODI_century} days since Joe Root's last ODI century.\n"
#             f"{days_elapsed_since_stokes_last_century} days since Ben Stokes' last century.\n"
#             f"{days_elapsed_since_stokes_last_test_century} days since Ben Stokes' last Test century.\n"
#             f"{days_elapsed_since_stokes_last_test_century_in_winning_cause} days since Ben Stokes' last Test century in a winning cause.\n"
#             f"This was tweeted at {timestamp}"
#         )
        
#         client.create_tweet(text=tweet_text)
#         print(f"Tweeted successfully!")

#     except Exception as e:
#         print(f"Error while tweeting: {e}")


    
# if __name__ == "__main__":
#     try:
#         user = client.get_me()
#         print(f"Authenticated as: {user.data['username']}")
#         daily_tweet()
#     except Exception as e:
#          print(f"Error: {e}")
