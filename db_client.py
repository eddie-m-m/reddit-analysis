import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")


class DBClient:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            print("Connecting to PostgreSQL database...")
            self.conn = psycopg2.connect(db_url)

            self.cursor = self.conn.cursor()

            print("Connection successful!")

            return self

        except Exception as e:
            print(f"Error occurred during connection: {e}")

            raise

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            if self.cursor:
                self.conn.rollback()
            print(
                f"An exception occured: {exception_value}. Rolling back transaction..."
            )
        else:
            if self.conn:
                self.conn.commit()

        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
