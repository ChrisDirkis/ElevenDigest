# Eleven Digest
Eleven digest is a email digest creator, for people who want to follow the top content of an account or a few accounts.

## How to use

- Make an `.env` file, based off of `.env.sample`, filling out each environment variable
- Make an `accounts.txt` file, with each line being a Twitter account you wish to have included in the digest (one per line, no @)
- Make an `addresses.txt` file, with each line being an email address to send the digest to (one per line)
- (Optional) Modify `email_template.html` and `tweet_template.html` as you please. 
    - In the email template, `{{names}}` will be substituted with a list of names of Twitter users, and `{{tweets}}` will be substituted with the tweets, generated using the tweet template
    - In the tweet template, `{{name}}` will be substituted with the name of the Twitter user, `{{url}}` with a link to the tweet, and `{{tweet}}` with the text of the tweet
- (Optional) Set up a python virtual environment (I recommend `python3 -m venv env`)
- Install the required packages using `pip3 install -r requirements.txt`
- Run using `python3 elevendigest.py`
- (Optional) Set up a cron job or systemd service and timer. I've chosen the latter, personally, running at 8am every Wednesday morning

Some sample files have been provided to ease in setup, but feel free to modify as you wish.

## Known issues

Feel free to fork and/or make PRs about these, or any other issues you find

- Does not handle "no new tweets in time period" case, at all.
- Tweet selection algorithm just looks at favourites, and doesn't look for "outlier tweets" but just cycles through the most popular ones by each account. There's definitely room for improvement here, and I'd be interested in any ideas.
- Reply ergonomics are bad
- No images