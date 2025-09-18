from get_comments_praw import get_comments_praw
from get_posts_praw import get_posts_praw
from db_handler import connect_to_db
import praw
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
client_user_agent = os.getenv("REDDIT_USER_AGENT")

db_url = os.getenv("DATABASE_URL")


def main():
    try:
        reddit_client = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=client_user_agent,
        )
        subreddit = reddit_client.subreddit("dataisbeautiful")

        for submission in subreddit.top(limit=3):
            print(f" - {submission.title} (Score: {submission.score})")

    except Exception as e:
        print(f"error: {e}")

    connect_to_db(db_url)


if __name__ == "__main__":
    main()
