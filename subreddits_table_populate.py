import tqdm
from datetime import datetime
from praw_client import PrawClient
from db_client import DBClient
from config import SUBREDDITS, DB_URL


def subreddits_table_populate(praw_client, db_client, subreddits):
    query = """
            INSERT INTO subreddits
            (subreddit, :member_count, :member_count_date, :collection_date) 
            VALUES (:subreddit, :member_count, :member_count_date, :collection_date)
            ON CONFLICT(subreddit) DO UPDATE SET
                member_count = EXCLUDED.member_count,
                member_count_date = EXCLUDED.member_count_date,
                collection_date EXCLUDED.collection_date;
        """

    now = datetime.now()
    data = []

    for subreddit in tqdm(subreddits, desc="Overall Progress"):
        try:
            subreddit = praw_client.reddit.subreddit(subreddit)
            member_count = subreddit.subscribers

            data.append(
                {
                    "subreddit": subreddit,
                    "member_count": member_count,
                    "member_count_date": now,
                    "collection_date": now,
                }
            )
        except Exception as e:
            print(f"Skipping subreddit r/{subreddit}. Error fetching data: {e}")
            continue

    if not data:
        print("No valid subreddit data to insert/update.")
        return

    try:
        print(f"Executing query to insert/update {len(data)} rows...")
        row_count = db_client.execute(query, data)
        print(f"{row_count} rows were inserted/updated successfully.")

    except Exception as e:
        print(f"Error occurred trying to populate subreddits table: {e}")


praw_client = PrawClient()
db_client = DBClient(DB_URL)

subreddits_table_populate(
    praw_client=praw_client, db_client=db_client, subreddits=SUBREDDITS
)
