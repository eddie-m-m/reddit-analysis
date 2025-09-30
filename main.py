# from db_handler import connect_to_db
# from dotenv import load_dotenv
# load_dotenv()
# db_url = os.getenv("DATABASE_URL")

from praw_client import PrawClient


def main():
    try:
        praw_client = PrawClient()
        reddit_instance = praw_client.reddit_instance()

        subreddit = reddit_instance.subreddit("dataisbeautiful")

        for submission in subreddit.top(limit=3):
            print(f" - {submission.title} (Score: {submission.score})")

    except Exception as e:
        print(f"error: {e}")

    # connect_to_db(db_url)


if __name__ == "__main__":
    main()
