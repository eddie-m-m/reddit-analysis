from datetime import datetime
from db_client import DBClient
from config import SUBREDDITS, DB_URL


def populate_subreddits_table(db_client, subreddits):
    query = """
            INSERT INTO subreddits
            (subreddit, collection_date)
            VALUES (:subreddit, :collection_date);
        """

    try:
        now = datetime.now()
        data = [
            {"subreddit": subreddit, "collection_date": now} for subreddit in subreddits
        ]

        print("Executing query...")
        row_count = db_client.execute(query, data)

        print(f"{row_count} rows were inserted successfully")

    except Exception as e:
        print(f"Error occurred trying to popupate subreddits table: {e}")


populate_subreddits_table(db_client=DBClient(DB_URL), subreddits=SUBREDDITS)
