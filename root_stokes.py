import tweepy
import os
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup

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

# -------------------- Utilities --------------------

def load_last_recorded_date(filename):
    try:
        with open(filename, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

def update_recorded_date(filename, new_date):
    with open(filename, "w") as f:
        f.write(new_date.strftime("%Y-%m-%d"))

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

# -------------------- URLs & Files --------------------

urls = {
    "root_odi": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=2;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "root_test": "https://stats.espncricinfo.com/ci/engine/player/303669.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_test": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_all": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=11;filter=advanced;orderby=start;orderbyad=reverse;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings",
    "stokes_winning": "https://stats.espncricinfo.com/ci/engine/player/311158.html?class=1;filter=advanced;orderby=start;orderbyad=reverse;result=1;runsmin1=100;runsval1=runs;template=results;type=batting;view=innings"
}

# Hardcoded fallback milestone dates
milestone_dates = {
    "root_test": date(2025, 8, 3),
    "root_odi": date(2025, 9, 7),
    "stokes_test": date(2025, 7, 26),
    "stokes_all": date(2025,7, 26),
    "stokes_winning": date(2022, 8, 26),
}

# -------------------- Logic --------------------

for key in urls:
    latest_start_date = fetch_latest_start_date(urls[key])
    if not latest_start_date:
        continue

    # File paths
    start_file = f"{key}_start.txt"
    detected_file = f"{key}_detected.txt"

    # Load existing records
    last_known_start = load_last_recorded_date(start_file)
    last_detected_date = load_last_recorded_date(detected_file)

    fallback_date = milestone_dates[key]

    if last_known_start is None or last_detected_date is None:
        # First time: store both files using hardcoded date
        update_recorded_date(start_file, fallback_date)
        update_recorded_date(detected_file, fallback_date)
        milestone_dates[key] = fallback_date
        continue

    if latest_start_date != last_known_start:
        # Only accept a change if it’s clearly a new match, not a reordering
        if abs((latest_start_date - last_known_start).days) > 5:
            print(f"[{key}] Detected new century (start: {latest_start_date}) → marking today as detection.")
            update_recorded_date(start_file, latest_start_date)
            update_recorded_date(detected_file, date.today())
            milestone_dates[key] = date.today()
        else:
            # Ignore tiny date shifts (edge cases)
            milestone_dates[key] = last_detected_date
    else:
        # No change
        milestone_dates[key] = last_detected_date

# -------------------- Tweet --------------------

def daily_tweet():
    today = date.today()
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Build Root block
    root_block = [
        ((today - milestone_dates['root_test']).days, "Joe Root's last Test century"),
        ((today - milestone_dates['root_odi']).days, "Joe Root's last ODI century")
    ]
    root_block.sort(key=lambda x: x[0])  # sort by days
    
    # Build Stokes block
    stokes_block = [
        ((today - milestone_dates['stokes_test']).days, "Ben Stokes' last Test century"),
        ((today - milestone_dates['stokes_winning']).days, "Ben Stokes' last Test century in a winning cause")
    ]
    stokes_block.sort(key=lambda x: x[0])  # sort by days
    
    # Combine into tweet
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
