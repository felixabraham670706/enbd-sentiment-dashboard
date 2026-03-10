import praw
import pandas as pd
import re
from openai import OpenAI
import os
import streamlit as st
from datetime import datetime, timedelta, timezone

# ==========================
# API KEYS
# ==========================

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=api_key)

# ==========================
# REDDIT CONNECTION
# ==========================

reddit = praw.Reddit(
    client_id="Sluh_7-LceBQjGQ3i61INg",
    client_secret="8LBSwWgIzYEvCitUWz56zL28qf0gQQ",
    user_agent="reddit_sentiment_bot"
)

# ==========================
# KEYWORDS
# ==========================

emirates_keywords = [
    "Emirates NBD",
    "Emirates bank",
    "ENBD",
    "EmiratesNBD"
]

# ==========================
# TIME WINDOW (LAST 2 DAYS)
# ==========================

now = datetime.now(timezone.utc)

two_days_ago = now - timedelta(days=1)

after = int(two_days_ago.timestamp())
before = int(now.timestamp())

# ==========================
# CLEAN TEXT
# ==========================

def clean_text_list(posts):

    cleaned = []

    for p in posts:

        text = re.sub(r"http\S+|@\w+|[^A-Za-z0-9\s]", "", str(p))
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 5:
            cleaned.append(text)

    return cleaned

# ==========================
# SENTIMENT CLASSIFICATION
# ==========================

def classify_sentiment(text):

    prompt = f"""
    Classify sentiment of the comment.

    Return ONLY one word:

    Positive
    Neutral
    Negative

    Comment:
    {text}
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text.strip()

# ==========================
# FETCH REDDIT COMMENTS
# ==========================

def fetch_last_two_days_comments(keywords, limit=10):

    comments_list = []

    for keyword in keywords:

        print("Searching for keyword:", keyword)

        for submission in reddit.subreddit("all").search(keyword, sort="new", limit=limit):

            submission.comments.replace_more(limit=0)

            for comment in submission.comments.list():

                if hasattr(comment, "created_utc"):

                    if after <= comment.created_utc <= before:

                        comments_list.append(comment.body.strip())

    return comments_list

# ==========================
# MAIN PIPELINE
# ==========================

def run_pipeline():

    print("Pipeline started")

    posts = fetch_last_two_days_comments(emirates_keywords, limit=10)

    print("Total comments fetched:", len(posts))

    cleaned = clean_text_list(posts)

    sentiments = []

    for c in cleaned:

        print("Classifying:", c[:40])

        try:
            s = classify_sentiment(c)

        except:
            s = "Neutral"

        sentiments.append(s)

    df = pd.DataFrame({
        "comment": cleaned,
        "sentiment": sentiments
    })

    print("Pipeline finished")

    return df