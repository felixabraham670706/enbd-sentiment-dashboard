import praw
import pandas as pd
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=api_key)

reddit = praw.Reddit(
    client_id="Sluh_7-LceBQjGQ3i61INg",
    client_secret="8LBSwWgIzYEvCitUWz56zL28qf0gQQ",
    user_agent="reddit_sentiment_bot"
)

def clean_text_list(posts):

    cleaned = []

    for p in posts:
        text = re.sub(r"http\S+|@\w+|[^A-Za-z0-9\s]", "", str(p))
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 5:
            cleaned.append(text)

    return cleaned


def classify_sentiment(text):

    prompt = f"""
    Classify sentiment of the comment.

    Return only one word:

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


def run_pipeline():
    print("Pipeline started")

    posts = []

    for submission in reddit.subreddit("all").search("Emirates NBD", limit=2):
        print("Fetching comments from post")

        submission.comments.replace_more(limit=0)

        for comment in submission.comments.list():
            posts.append(comment.body)
    print("Total comments fetched:", len(posts))
    cleaned = clean_text_list(posts)

    sentiments = []

    for c in cleaned:
        print("Classifying:", c[:30])


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