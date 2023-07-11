#!/usr/bin/env python3

from collections import Counter
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
import praw

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = os.getenv("USER_AGENT")

if len(sys.argv) < 2:
    print("Usage: python reddit.py <subreddit> [limit=1000] [count=10]")
    sys.exit(1)

subreddit_name = sys.argv[1].replace("r/", "", 1)

def get_int_arg(arg_index, default):
    if len(sys.argv) > arg_index:
        try:
            return int(sys.argv[arg_index])
        except ValueError:
            print(f"Argument {arg_index} must be an integer")
            sys.exit(1)
    return default

limit = get_int_arg(2, 1000)
count = get_int_arg(3, 10)

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)

subreddit = reddit.subreddit(subreddit_name)

domain_blocklist = [
    "reddit.com",
    "redd.it",
    "imgur.com",
]
domains = []
for submission in subreddit.new(limit=limit):
    domain = urlparse(submission.url).netloc
    if not domain or any(blocked in domain for blocked in domain_blocklist):
        continue
    domains.append(domain)

counter = Counter(domains)

with open(f"{subreddit_name}-top-{count}.csv", "w") as f:
    print("domain,count", file=f)
    print(f"r/{subreddit_name} top {count} domains from last {limit} submissions:")
    for domain, count in counter.most_common(count):
        print(f"{domain}: {count}")
        print(f"{domain},{count}", file=f)
