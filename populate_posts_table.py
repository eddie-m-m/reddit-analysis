import logging
from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine
from db_client import DBClient
from praw_client import PrawClient
from config import SUBREDDITS, DB_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.FileHandler("posts_collection.log"), logging.StreamHandler()],
)


def get_subreddit_id(db_client, subreddit):
    query = """
        SELECT subreddit_id
        FROM subreddits
        WHERE subreddit = :subreddit
    """
    params = {"subreddit": subreddit}

    result = db_client.fetch_all(query, params)

    if result:
        return result[0]["subreddit_id"]
    else:
        raise ValueError(
            f"Subreddit 'r/{subreddit}' not found in the database. "
            "Pre-populate before running this script."
        )


def get_posts(praw_client, db_client, sql_engine, subreddits, limit, time_interval):
    total_new_posts = 0
    for subreddit in tqdm(subreddits, desc="Overall Progress"):
        try:
            logging.info(f"--- Starting collection for r/{subreddit} ---")

            subreddit_id = get_subreddit_id(db_client, subreddit)

            subreddit = praw_client.reddit.subreddit(subreddit)
            top_posts = subreddit.top(limit=limit, time_filter=time_interval)

            posts = []
            top_posts_iter = tqdm(top_posts, desc=f"f/{subreddit}", leave=False)

            for post in top_posts_iter:
                posts.append(
                    {
                        "post_id": post.id,
                        "subreddit_id": subreddit_id,
                        "title": post.title,
                        "flair": post.link_flair_text,
                        "selftext": post.selftext,
                        "url": post.url,
                        "author": post.author.name if post.author else "[deleted]",
                        "created_utc": pd.to_datetime(
                            post.created_utc, unit="s", utc=True
                        ),
                        "score": post.score,
                        "num_comments": post.num_comments,
                    }
                )

            if not posts:
                logging.warning(f"No posts found for r/{subreddit}. Skipping.")
                continue

            df = pd.DataFrame(posts)
            df.to_sql(name="posts", con=sql_engine, if_exists="append", index=False)

            inserted_count = len(df)
            total_new_posts += inserted_count

            logging.info(
                f"Completed r/{subreddit}. "
                f"Fetched {len(posts)} posts from API. "
                f"Inserted {inserted_count} new posts into the database."
            )

        except Exception as e:
            logging.error(
                f"An error occurred while processing r/{subreddit}: {e}",
                exc_info=True,
            )

    logging.info("--- FINISHED ---")
    logging.info(f"Total new posts inserted across all subreddits: {total_new_posts}")


praw_client = PrawClient()
db_client = DBClient(DB_URL)
sql_engine = create_engine(DB_URL)

try:
    get_posts(
        praw_client=praw_client,
        db_client=db_client,
        sql_engine=sql_engine,
        subreddits=SUBREDDITS,
        limit=1000,
        time_interval="year",
    )
except Exception as e:
    logging.critical(f"A critical error stopped the script: {e}", exc_info=True)
finally:
    logging.info("Finished")
