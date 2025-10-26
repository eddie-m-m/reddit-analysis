from tqdm import tqdm
import logging
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from clients import DBClient
from config import DB_URL

log_file_name = "sentiment_analysis_populate.log"
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
    logging.info("Fetching new comments for sentiment analysis...")

    query = """
    SELECT c.comment_id, c.body
    FROM comments AS c
    LEFT JOIN sentiment_analysis AS sa ON c.comment_id = sa.comment_id
    WHERE sa.analysis_id IS NULL;
    """

    comments = db_client.fetch_all(query)

    logging.info(f"Found {len(comments)} new comments to analyze.")
    return comments


def bulk_insert_sentiments(db_client, results_data):
    if not results_data:
        logging.info("No new sentiment results to insert.")
        return 0

    insert_query = """
    INSERT INTO sentiment_analysis 
    (comment_id, vader_compound, vader_positive, vader_negative, vader_neutral) 
    VALUES (:comment_id, :vader_compound, :vader_positive, :vader_negative, :vader_neutral)
    ON CONFLICT (comment_id) DO NOTHING; 
    """

    try:
        row_count = db_client.execute(insert_query, results_data)
        logging.info(f"Successfully inserted {row_count} new sentiment analysis rows.")
        return row_count
    except Exception as e:
        logging.error(f"Error during bulk sentiment insert: {e}", exc_info=True)
        return 0


def sentiment_analysis_populate(db_client):
    comments = get_comments(db_client)

    if not comments:
        logging.info("No new comments to process. Exiting.")
        return

    logging.info("Running VADER...")
    analyzer = SentimentIntensityAnalyzer()
    results_data = []

    for comment in tqdm(comments, desc="Analyzing Comments"):
        scores = analyzer.polarity_scores(comment["body"])

        results_data.append(
            {
                "comment_id": comment["comment_id"],
                "vader_compound": scores["compound"],
                "vader_positive": scores["pos"],
                "vader_negative": scores["neg"],
                "vader_neutral": scores["neu"],
            }
        )

    bulk_insert_sentiments(db_client, results_data)


db_client = DBClient(DB_URL)

try:
    sentiment_analysis_populate(db_client=db_client)
except Exception as e:
    logging.critical(f"A critical error stopped the script: {e}", exc_info=True)
finally:
    logging.info("--- VADER SENTIMENT ANALYSIS SCRIPT FINISHED ---")
