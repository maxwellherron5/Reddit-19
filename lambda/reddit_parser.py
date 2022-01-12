import json
import praw
import datetime
import os


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
)

# This is the day that data collection began. It will be used to calculate
# the offset necessary to determine which row of the CSV to plot.
start_day = datetime.date(2020, 4, 28)


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
    print("*" * 80)
    print(
        " " * 10
        + "Running COVID-19 keyword mention scan for "
        + str(datetime.date.today())
    )
    print("*" * 80 + "\n")
    print("-" * 80)
    for subreddit in subreddits:
        print("Scanning r/" + subreddit + "\n")
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
                    print(submission.title + "\n")
        output[subreddit] = count
        print(
            "Total mentions of COVID-19 related keywords in r/" + subreddit + ":", count
        )
        print("-" * 80)
    return output
    # write_output(output)


# def write_output(output):
#     """
#     Writes the output dictionary generated from run_bot() to the existing CSV
#     """
#     with open("/Users/maxwell/Documents/workspace/CoronaScan/results.csv", 'a') as f:
#         writer = csv.writer(f)
#         print("Now writing output to results.csv . . .")
#         values = list(output.values())
#         values.insert(0, datetime.date.today())
#         writer.writerow(values)
#         print("Finished writing output!")


def get_offset():
    """
    Calculates the integer offset between the start day of data collection,
    and the current day. This is then used to determine which line of the CSV
    to generate the plot from.
    """
    offset = datetime.date.today() - start_day
    return int(offset.days) - 4


def handler(event, context):
    print("request: {}".format(json.dumps(event)))
    bot = bot_login()
    output = run_bot(bot)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": f"{output}",
    }
