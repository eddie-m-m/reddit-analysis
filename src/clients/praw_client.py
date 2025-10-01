import praw
import os
from dotenv import load_dotenv

load_dotenv()


class PrawClient:
    def __init__(self):
        try:
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            client_user_agent = os.getenv("REDDIT_USER_AGENT")

            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=client_user_agent,
            )

        except Exception as e:
            print(f"Error occurred during PRAW init: {e}")
            self.reddit = None

    def reddit_instance(self):
        return self.reddit
