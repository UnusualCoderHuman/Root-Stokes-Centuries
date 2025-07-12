import tweepy
import os
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup

# --- Twitter API setup ---
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

# --- Read and write utility functions ---
def load_last_known_start_date(filename):
    try:
        with open(filename, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

def save_last_known_start_date(filename, new_date):
    with open(filename, "w") as f:
        f.write(new_date.strftime("%Y-%m-%d"))

def load_detection_date(filename):
    try:
        with open(filename, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

def save_detection_date(filename, date_value):
    with open(filename, "w") as f:
        f.write(date_value.strftime("%Y-%m-%d"))

# --- Fetch latest match start date from Cricinfo ---
def fetch_latest_start_date(url):
    headers = { "User-Agent": "Mozilla/5.0" }
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

# --- URLs for stats pages ---
urls = {
    "root_odi": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=2;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "root_test": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_test": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_all": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=11;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_winning": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;result=1;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings"
}

# --- Filenames for storing start dates and detection dates ---
start_date_files = {
    "root_odi": "root_odi_start.txt",
    "root_test": "root_test_start.txt",
    "stokes_test": "stokes_test_start.txt",
    "stokes_all": "stokes_all_start.txt",
    "stokes_winning": "stokes_winning_start.txt"
}

detection_date_files = {
    "root_odi": "root_odi_detected.txt",
    "root_test": "root_test_detected.txt",
    "stokes_test": "stokes_test_detected.txt",
    "stokes_all": "stokes_all_detected.txt",
    "stokes_winning": "stokes_winning_detected.txt"
}

# --- Default hardcoded milestone detection dates ---
milestone_dates = {
    "root_test": date(2025, 7, 11),
    "root_odi": date(2025, 6, 1),
    "stokes_test": date(2023, 7, 2),
    "stokes_all": date(2023, 11, 8),
    "stokes_winning": date(2022, 8, 26)
}

# --- Check and update milestone detection dates ---
for key in urls:
    latest_start_date = fetch_latest_start_date(urls[key])
    if not latest_start_date:
        continue

    last_known_start = load_last_known_start_date(start_date_files[key])
    detection_date = load_detection_date(detection_date_files[key])

    if last_known_start is None or latest_start_date != last_known_start:
        # New match found — update detection date to today
        print(f"[{key}] New century detected. Updating detection date to today: {date.today()}")
        milestone_dates[key] = date.today()
        save_last_known_start_date(start_date_files[key], latest_start_date)
        save_detection_date(detection_date_files[key], date.today())
    else:
        # Use previously stored detection date or fallback to hardcoded
        if detection_date:
            milestone_dates[key] = detection_date
        else:
            milestone_dates[key] = milestone_dates[key]  # fallback to hardcoded

# --- Tweeting function ---
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

# --- Main run ---
if __name__ == "__main__":
    try:
        user = client.get_me()
        print(f"Authenticated as: {user.data['username']}")
        daily_tweet()
    except Exception as e:
        print(f"Error: {e}")
