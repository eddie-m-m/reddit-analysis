import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

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
    conn = None
    query = """
            INSERT INTO subreddits
            (subreddit, collection_date)
            VALUES (%s, %s);
        """
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        print("Connection successful!")

        cursor = conn.cursor()

        now = datetime.now()
        data = [(subreddit, now) for subreddit in subreddits]

        print("Executing query...")
        cursor.executemany(query, data)

        conn.commit()
        print(f"{cursor.rowcount} rows were inserted successfully")

        cursor.close()

    except psycopg2.Error as e:
        print(f"Error connecting to or interacting with the database: {e}")

        if conn:
            conn.rollback()

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


populate_subreddits_table(subreddits=subreddits)
