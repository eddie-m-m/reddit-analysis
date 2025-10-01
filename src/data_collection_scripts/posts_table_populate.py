import logging
import os
from datetime import datetime, timezone
from tqdm import tqdm
from clients import DBClient, PrawClient
from config import SUBREDDITS, DB_URL

log_file_name = "posts_table_populate.log"
log_dir = os.path.join("logs", "scripts")
log_path = os.path.join(log_dir, log_file_name)

os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(),
    ],
)


def fetch_diverse_posts(subreddit, limit, time_interval):
    logging.info(f"Fetching diverse posts for r/{subreddit.display_name}...")

    posts = {}

    try:
        for post in subreddit.top(limit=limit, time_filter=time_interval):
            posts[post.id] = post
    except Exception as e:
        logging.warning(
            f"Could not fetch 'top' posts for r/{subreddit.display_name}: {e}"
        )

    try:
        for post in subreddit.hot(limit=limit):
            posts[post.id] = post
    except Exception as e:
        logging.warning(
            f"Could not fetch 'hot' posts for r/{subreddit.display_name}: {e}"
        )

    try:
        for post in subreddit.new(limit=limit):
            posts[post.id] = post
    except Exception as e:
        logging.warning(
            f"Could not fetch 'new' posts for r/{subreddit.display_name}: {e}"
        )

    try:
        for post in subreddit.controversial(limit=limit, time_filter=time_interval):
            posts[post.id] = post
    except Exception as e:
        logging.warning(
            f"Could not fetch 'controversial' posts for r/{subreddit.display_name}: {e}"
        )

    logging.info(f"Found {len(posts)} unique posts across categories.")

    return list(posts.values())


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


def bulk_upsert_posts(db_client, posts):
    if not posts:
        return 0

    query = """
        INSERT INTO posts (
            post_id, subreddit_id, author_fullname, title, selftext, url, 
            flair, created_utc, score, num_comments, upvote_ratio, stickied
        )
        VALUES (
            :post_id, :subreddit_id, :author_fullname, :title, :selftext, :url, 
            :flair, :created_utc, :score, :num_comments, :upvote_ratio, :stickied
        )
        ON CONFLICT (post_id) DO NOTHING
    """

    row_count = db_client.execute(query, posts)
    return row_count


def get_subreddit_id(db_client, subreddit):
    query = """
        SELECT subreddit_id
        FROM subreddits
        WHERE subreddit = :subreddit
    """
    params = {"subreddit": subreddit}

    result = db_client.fetch_one(query, params)

    if result:
        return result["subreddit_id"]
    else:
        raise ValueError(f"Subreddit 'r/{subreddit}' not found in the database. ")


def get_existing_post_ids(db_client, subreddit_id):
    query = """SELECT post_id
    FROM posts
    WHERE subreddit_id = :subreddit_id
    """

    params = {"subreddit_id": subreddit_id}
    result = db_client.fetch_all(query, params)

    return {row["post_id"] for row in result}


def posts_table_populate(praw_client, db_client, subreddits, limit, time_interval):
    total_new_posts = 0
    for subreddit in tqdm(subreddits, desc="Overall Progress"):
        try:
            logging.info(f"--- Starting collection for r/{subreddit} ---")

            subreddit_id = get_subreddit_id(db_client, subreddit)

            existing_post_ids = get_existing_post_ids(db_client, subreddit_id)

            subreddit = praw_client.reddit.subreddit(subreddit)
            all_posts = fetch_diverse_posts(
                subreddit, limit=limit, time_interval=time_interval
            )

            posts = []
            authors = {}

            all_posts_iter = tqdm(all_posts, desc=f"f/{subreddit}", leave=False)

            for post in all_posts_iter:
                if post.id in existing_post_ids:
                    continue

                if post.author:
                    authors[post.author_fullname] = post.author.name
                    author_fullname = post.author_fullname
                else:
                    author_fullname = None

                posts.append(
                    {
                        "post_id": post.id,
                        "subreddit_id": subreddit_id,
                        "author_fullname": author_fullname,
                        "title": post.title,
                        "flair": post.link_flair_text,
                        "selftext": post.selftext,
                        "url": post.url,
                        "created_utc": datetime.fromtimestamp(
                            post.created_utc, tz=timezone.utc
                        ),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "upvote_ratio": post.upvote_ratio,
                        "stickied": post.stickied,
                    }
                )

            if not posts:
                logging.warning(f"No posts found for r/{subreddit}. Skipping.")
                continue

            bulk_upsert_authors(db_client, authors)

            inserted_count = bulk_upsert_posts(db_client, posts)
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

try:
    posts_table_populate(
        praw_client=praw_client,
        db_client=db_client,
        subreddits=SUBREDDITS,
        limit=None,
        time_interval="all",
    )
except Exception as e:
    logging.critical(f"A critical error stopped the script: {e}", exc_info=True)
finally:
    logging.info("Finished")
