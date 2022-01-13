import json
import praw
import datetime
import os

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


def bot_login():
    """This function logs in the bot account that I am using to access Reddit."""
    bot = praw.Reddit(
        username=os.environ.get("BOT_USERNAME"),
        password=os.environ.get("BOT_PASSWORD"),
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent="My COVID-19 mention scanning bot",
    )
    return bot


def run_bot(bot):
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
        current = bot.subreddit(subreddit)
        cutoff_time = datetime.date.today() - datetime.timedelta(1)
        cutoff_time = float(cutoff_time.strftime("%s"))
        for submission in current.new():
            if submission.created_utc > cutoff_time:
                current_title = submission.title.lower()
                keyword_check = (
                    "coronavirus" in current_title
                    or "covid" in current_title
                    or "pandemic" in current_title
                    or "quarantine" in current_title
                )
                if keyword_check:
                    count += 1
        output[subreddit] = count
        logger.info(
            f"Total mentions of COVID-19 related keywords in r/{subreddit}: {count}"
        )
    return output


# def write_output(output):
#     """
#     Writes the output dictionary generated from run_bot() to the existing CSV
#     """
#     with open("/Users/maxwell/Documents/workspace/CoronaScan/results.csv", 'a') as f:
#         writer = csv.writer(f)
#         logger.info("Now writing output to results.csv . . .")
#         values = list(output.values())
#         values.insert(0, datetime.date.today())
#         writer.writerow(values)
#         logger.info("Finished writing output!")


def handler(event, context):
    logger.info("request: {}".format(json.dumps(event)))
    bot = bot_login()
    output = run_bot(bot)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": f"{output}",
    }
