import twitter
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from itertools import groupby

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

datetimeformat = "%a %b %d %H:%M:%S %z %Y"

def get_tweets(api, accounts, offset):
    now = datetime.now(tz=timezone.utc)
    earliest = now - offset

    tweets = []

    for account in accounts:
        tweets_by_account = []
        max_id = None
        while True:
            # always returns at least one tweet, unless the listed acc has 0 tweets
            tweets = api.GetUserTimeline(screen_name=account, count=200, max_id=max_id)
            relevant_tweets = [tweet for tweet in tweets if datetime.strptime(tweet.created_at, datetimeformat) > earliest]
            
            if len(relevant_tweets) == 0:
                break

            new_max_id = min(relevant_tweets, key=lambda x: x.id).id
            if (new_max_id == max_id):
                break
            max_id = new_max_id

            tweets_by_account += relevant_tweets

        tweets += tweets_by_account
    
    return tweets


def filter_tweets(tweets):
    # filter tweets that are replying to users or other tweets
    return [t for t in tweets if not t.in_reply_to_user_id and not t.in_reply_to_status_id]

def choose_tweets(tweets, thread_count):
    # group tweets by user
    groups = [list(group) for _, group in groupby(tweets, lambda x: x.id)]

    # sort each group by fav count
    for group in groups:
        group.sort(key=lambda x: x.favorite_count)

    chosen = []
    while len(groups) > 0:
        # sort each group by max fav count
        groups.sort(reverse=True, key=lambda group: group[0].favorite_count)

        # pick tweets until we hit thread_count
        for group in groups:
            chosen.append(group[0])
            if len(chosen) == thread_count:
                return chosen

        # remove picked tweets
        groups = [group[1:] for group in groups if len(group) > 1]

    # we didn't have enough tweets, so just return the ones we got
    return chosen

def main():
    load_dotenv()

    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
    TWITTER_ACCESS_TOKEN_KEY = os.getenv("TWITTER_ACCESS_TOKEN_KEY")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    SENDGRID_API_KEY=os.getenv("SENDGRID_API_KEY")

    FROM_EMAIL=os.getenv("FROM_EMAIL")

    THREAD_COUNT=int(os.getenv("THREAD_COUNT"))
    OFFSET_IN_DAYS=int(os.getenv("OFFSET_IN_DAYS"))
    offset = timedelta(days=OFFSET_IN_DAYS)

    api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                      consumer_secret=TWITTER_CONSUMER_SECRET,
                      access_token_key=TWITTER_ACCESS_TOKEN_KEY,
                      access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    remove_endline = lambda x: x[:-1] if x[-1] == "\n" else x
    addresses = [remove_endline(line) for line in open("addresses.txt").readlines()]
    accounts = [remove_endline(line) for line in open("accounts.txt").readlines()]

    # get tweets
    tweets = get_tweets(api, accounts, offset)    
    
    # filter tweets
    filtered_tweets = filter_tweets(tweets)

    # pick good tweets
    chosen_tweets = choose_tweets(filtered_tweets, THREAD_COUNT)

    # send emails
    print(f"sending emails to [{', '.join(addresses)}]")

    # TODO update email content
    email_content = "\n".join((f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}" for tweet in chosen_tweets))
    for address in addresses: 
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=address,
            subject="Eleven Digest Update",
            plain_text_content = email_content,
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            # TODO Actually handle errors maybe?
            print(e)


if __name__ == "__main__":
    main()