import logging
import pandas as pd
from tqdm import tqdm
from sqlalchemy import create_engine
from db_client import DBClient
from praw_client import PrawClient
from config import SUBREDDITS, DB_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.FileHandler("comments_collection.log"), logging.StreamHandler()],
)


def bulk_upsert_authors(db_client, authors):
    if not authors:
        return

    author_list = [
        {"fullname": fullname, "name": name} for fullname, name in authors.items()
    ]

    query = """
        INSERT INTO authors (author_fullname, author_name)
        VALUES (:fullname, :name)
        ON CONFLICT (author_fullname) DO NOTHING
    """

    db_client.execute(query, author_list)
    logging.info(f"Bulk upserted {len(author_list)} unique authors.")


def get_subreddit_id(db_client, subreddit):
    query = """SELECT subreddit_id
    FROM subreddits
    WHERE subreddit = :subreddit
    """

    params = {"subreddit": subreddit}
    result = db_client.fetch_one(query, params)

    if result:
        return result["subreddit_id"]
    else:
        raise ValueError(f"Subreddit 'r/{subreddit}' not found in the database.")


def get_post_ids_for_subreddit(db_client, subreddit_id):
    query = "SELECT post_id FROM posts WHERE subreddit_id = :subreddit_id"

    params = {"subreddit_id": subreddit_id}
    result = db_client.fetch_all(query, params)

    return [row["post_id"] for row in result]


def get_processed_post_ids(db_client, subreddit_id):
    query = """
        SELECT DISTINCT p.post_id
        FROM posts p
        JOIN comments c ON p.post_id = c.post_id
        WHERE p.subreddit_id = :subreddit_id
    """

    params = {"subreddit_id": subreddit_id}
    result = db_client.fetch_all(query, params)

    return [row["post_id"] for row in result]


def populate_comments_table(
    praw_client, db_client, sql_engine, subreddits, batch_size=25
):
    total_new_comments = 0
    for subreddit_name in tqdm(subreddits, desc="Overall Progress"):
        try:
            logging.info(f"--- Starting comment collection for r/{subreddit_name} ---")

            subreddit_id = get_subreddit_id(db_client, subreddit_name)

            all_post_ids = get_post_ids_for_subreddit(db_client, subreddit_id)
            if not all_post_ids:
                logging.warning(
                    f"No posts found in database for r/{subreddit_name}. Skipping."
                )
                continue

            processed_post_ids = get_processed_post_ids(db_client, subreddit_id)

            posts_to_process = list(set(all_post_ids) - set(processed_post_ids))

            logging.info(
                f"Found {len(all_post_ids)} total posts. {len(processed_post_ids)} already processed."
            )
            if not posts_to_process:
                logging.info(
                    f"No new posts to process for r/{subreddit_name}. Skipping."
                )
                continue

            logging.info(
                f"Processing comments for {len(posts_to_process)} new posts..."
            )

            comments_in_batch = []
            authors_in_batch = {}

            post_ids_iter = tqdm(
                posts_to_process, desc=f"r/{subreddit_name}", leave=False
            )

            for idx, post_id in enumerate(post_ids_iter):
                try:
                    submission = praw_client.reddit.submission(id=post_id)
                    submission.comments.replace_more(limit=None)

                    for comment in submission.comments.list():
                        if not hasattr(comment, "body"):
                            continue

                        author_fullname = None
                        if comment.author:
                            author_fullname = comment.author_fullname
                            authors_in_batch[comment.author_fullname] = (
                                comment.author.name
                            )

                        comments_in_batch.append(
                            {
                                "comment_id": comment.id,
                                "post_id": post_id,
                                "author_fullname": author_fullname,
                                "parent_id": comment.parent_id,
                                "body": comment.body,
                                "created_utc": pd.to_datetime(
                                    comment.created_utc, unit="s", utc=True
                                ),
                                "score": comment.score,
                                "depth": comment.depth,
                                "is_submitter": comment.is_submitter,
                                "stickied": comment.stickied,
                            }
                        )
                except Exception as e:
                    logging.error(f"Could not process comments for post {post_id}: {e}")

                if (idx + 1) % batch_size == 0 or (idx + 1) == len(posts_to_process):
                    if not comments_in_batch:
                        continue

                    bulk_upsert_authors(db_client, authors_in_batch)

                    df = pd.DataFrame(comments_in_batch)
                    df.to_sql(
                        name="comments", con=sql_engine, if_exists="append", index=False
                    )

                    inserted_count = len(df)
                    total_new_comments += inserted_count
                    logging.info(
                        f"Saved a batch of {inserted_count} comments for r/{subreddit_name}."
                    )

                    comments_in_batch = []
                    authors_in_batch = {}

            logging.info(f"Completed r/{subreddit_name}.")

        except Exception as e:
            logging.error(
                f"An error occurred while processing r/{subreddit_name}: {e}",
                exc_info=True,
            )

    logging.info("--- FINISHED ---")
    logging.info(
        f"Total new comments inserted across all subreddits: {total_new_comments}"
    )


praw_client = PrawClient()
db_client = DBClient(DB_URL)
sql_engine = create_engine(DB_URL)

try:
    populate_comments_table(
        praw_client=praw_client,
        db_client=db_client,
        sql_engine=sql_engine,
        subreddits=SUBREDDITS,
        batch_size=25,
    )
except Exception as e:
    logging.critical(f"A critical error stopped the script: {e}", exc_info=True)
finally:
    logging.info("Comment collection script finished.")
