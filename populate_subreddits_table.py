from datetime import datetime
from db_client import DBClient

subreddits = [
    "dataisbeautiful",
    "SQL",
    "dataanalysis",
    "statistics",
    "datascience",
    "businessanalysis",
    "visualization",
    "dataengineering",
    "MachineLearning",
    "businessintelligence",
]


def populate_subreddits_table(subreddits):
    query = """
            INSERT INTO subreddits
            (subreddit, collection_date)
            VALUES (%s, %s);
        """

    try:
        with DBClient() as db:
            now = datetime.now()
            data = [(subreddit, now) for subreddit in subreddits]

            print("Executing query...")
            db.cursor.executemany(query, data)

            print(f"{db.cursor.rowcount} rows were inserted successfully")

    except Exception as e:
        print(f"Error occurred trying to popupate subreddits table: {e}")


populate_subreddits_table(subreddits=subreddits)
