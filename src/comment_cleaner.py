import logging
import os
import re
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm

from clients import DBClient
from config import DB_URL

log_file_name = "cleaned_comments_populate.log"
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


def get_comments(db_client):
    logging.info("Fetching new comments for cleaning...")

    # query = """
    # SELECT c.comment_id, c.body
    # FROM comments AS c
    # LEFT JOIN cleaned_comments AS cc ON c.comment_id = cc.comment_id
    # WHERE cc.comment_id IS NULL;
    # """
    # test query
    query = """
    SELECT c.comment_id, c.body
    FROM comments AS c
    LEFT JOIN cleaned_comments AS cc ON c.comment_id = cc.comment_id
    WHERE cc.comment_id IS NULL
    LIMIT 100;
    """

    comments = db_client.fetch_all(query)

    logging.info(f"Found {len(comments)} new comments to clean.")
    return comments


def clean_text(text, stop_words):
    # remove URLs
    text = re.sub(r"http\S+", "", text)
    # remove non-alpha chars
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = text.lower()
    tokens = text.split()
    # 5. Remove stopwords
    cleaned_tokens = [word for word in tokens if word not in stop_words]

    # for Information Density (ID) metric
    word_count = len(cleaned_tokens)

    cleaned_body = " ".join(cleaned_tokens)

    return cleaned_body, word_count


def bulk_insert_cleaned_comments(db_client, results_data):
    if not results_data:
        logging.info("No new cleaned comments to insert.")
        return 0

    insert_query = """
    INSERT INTO cleaned_comments 
    (comment_id, cleaned_body, word_count) 
    VALUES (:comment_id, :cleaned_body, :word_count)
    ON CONFLICT (comment_id) DO NOTHING; 
    """

    try:
        row_count = db_client.execute(insert_query, results_data)
        logging.info(f"Successfully inserted {row_count} new cleaned comments.")
        return row_count
    except Exception as e:
        logging.error(f"Error during bulk cleaned comment insert: {e}", exc_info=True)
        return 0


def cleaned_comments_populate(db_client, stop_words):
    comments = get_comments(db_client)

    if not comments:
        logging.info("No new comments to process. Exiting.")
        return

    logging.info("Cleaning comments...")
    results_data = []

    for comment in tqdm(comments, desc="Cleaning Comments"):
        cleaned_body, word_count = clean_text(comment["body"], stop_words)

        results_data.append(
            {
                "comment_id": comment["comment_id"],
                "cleaned_body": cleaned_body,
                "word_count": word_count,
            }
        )

    bulk_insert_cleaned_comments(db_client, results_data)


logging.info("--- STARTING CLEANED_COMMENTS POPULATE SCRIPT ---")

db_client = DBClient(DB_URL)  #

try:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        logging.info("Downloading NLTK stopwords package...")
        nltk.download("stopwords")

    stop_words = set(stopwords.words("english"))

    cleaned_comments_populate(db_client=db_client, stop_words=stop_words)
except Exception as e:
    logging.critical(f"A critical error stopped the script: {e}", exc_info=True)
finally:
    logging.info("--- CLEANED_COMMENTS POPULATE SCRIPT FINISHED ---")
