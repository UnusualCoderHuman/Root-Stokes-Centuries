# Root and Stokes Century Bot
A Twitter bot that tweets daily how many days since Root and Stokes' last international centuries.

## Origin
Root and Stokes are two of my favourite players. As a result, I thought it would be a fun side-project to create a bot similar to the ashes one tracking days since their last centuries and having it reset to 0 when they do score.

## What it tracks
Days since Root's last ODI and Test Century

Days since Stokes' last Test Century and Test Century in a winning cause (I noticed that in a winning cause was a surprisingly long time ago so thought it would be a fun thing to add)

## How it works
Built in Python using Tweepy (Twitter API wrapper). A scheduled script runs daily, calculates the number of days elapsed since two hardcoded dates and posts the update automatically. A timestamp is included in each tweet to ensure uniqueness and avoid spam detection. API credentials are stored as environment variables for security.

## Scheduling
Runs daily via a GitHub Actions cron job, scheduled for 07:50 UTC. 
Note: GitHub Actions cron jobs can experience delays of several hours due to queue times on shared infrastructure.

## Limitations
Dates are hardcoded and need updating whenever Root or Stokes scores a century. There is no reliable database that tracks the exact date of their century especially for Test matches where the best alternative is one that tracks the start date of the test (tests can last up to 5 days so the century could be on day 1 or day 5). Whilst scraping could be done for ODI's to ensure consistency I thought it would be better to remain consistent throughout.
Tweet timing may vary due to GitHub Actions queue delays

## Follow the bot
https://x.com/root_stokes_100

## Note
Stokes announced his retirement on 28th June 2026. The bot will be updated accordingly to remove him prior to England's next Test commitment.
