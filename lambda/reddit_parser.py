import json
import datetime
import time
import os
import requests

import praw
import boto3

from logger import get_logger

logger = get_logger()

subreddits = (
    "worldnews",
    "news",
    "funny",
    "gaming",
    "pics",
    "science",
    "videos",
    "AskReddit",
    "aww",
    "askscience",
    "Tinder",
    "BlackPeopleTwitter",
    "politics",
    "dankmemes",
    "memes",
    "PoliticalHumor",
    "WhitePeopleTwitter",
    "ABoringDystopia",
    "Conservative",
    "nottheonion",
    "LateStageCapitalism",
    "todayilearned",
    "futurology",
    "technology",
    "travel",
)

keywords = (
    "coronavirus",
    "covid",
    "pandemic",
    "quarantine",
    "lockdown",
    "variant",
    "outbreak",
    "virus",
    "epidemic",
    "delta",
    "omicron",
)


def bot_login() -> praw.Reddit:
    """This function logs in the bot account that I am using to access Reddit."""
    bot = praw.Reddit(
        username=os.environ.get("BOT_USERNAME"),
        password=os.environ.get("BOT_PASSWORD"),
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent="My COVID-19 mention scanning bot",
    )
    return bot


def run_bot(bot: praw.Reddit) -> dict:
    """
    Iterates through all subreddits in the subreddit list. It then parses through
    the 'new' section of the subreddit, and views all posts that are from the
    current day. If detects a mention of [coronavirus, covid, pandemic, quarantine],
    it will add one to the total count. It then sets that count as the value tied
    to the subreddit key in the dictionary.
    """
    output = {key: None for key in subreddits}
    for subreddit in subreddits:
        logger.info(f"Scanning r/{subreddit}")
        count = 0
        subreddit_data = get_historical_data(subreddit).get("data", None)
        if subreddit_data:
            logger.info(subreddit_data)
            for submission in subreddit_data:
                title = submission["title"].lower()
                if any(keyword in title for keyword in keywords):
                    count += 1

            output[subreddit] = count
            logger.info(
                f"Total mentions of COVID-19 related keywords in r/{subreddit}: {count}"
            )
        else:
            output[subreddit] = 0
    logger.info(f"Output: {output}")
    return output


def write_output(result: dict):
    """
    Writes the output dictionary generated from run_bot() to the existing CSV
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("KeywordCounts")
    logger.info("Writing output to DynamoDB...")
    table.put_item(
        Item={
            "results": json.dumps(result),
            "timestamp": datetime.today().strftime("%Y-%m-%d"),
        }
    )
    logger.info(f"Successfully wrote output to DynamoDB")


def get_historical_data(subreddit):
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=1)
    endpoint = f"https://api.pushshift.io/reddit/submission/search/?after={int(start_time.timestamp())}&before={int(end_time.timestamp())}&sort_type=score&sort=desc&subreddit={subreddit}"
    logger.info(f"Request: {endpoint}")
    res = requests.get(endpoint)
    logger.info(res.status_code)
    if res.status_code == 429:
        time.sleep(20)
        res = requests.get(endpoint)
    return res.json()


def handler(event, context):
    logger.info("request: {}".format(json.dumps(event)))
    bot = bot_login()
    output = run_bot(bot)
    write_output(output)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": f"{output}",
    }


if __name__ == "__main__":
    # get_historical_data("memes")
    bot = bot_login()
    output = run_bot(bot)
