from sqlalchemy import create_engine, text
from config import DB_URL


class DBClient:
    def __init__(self, db_url=DB_URL):
        try:
            self.engine = create_engine(db_url)
            print("Successful DBClient init")
        except Exception as e:
            print(f"Failed to create DB engine: {e}")
            raise

    def fetch_one(self, query, params=None):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result.mappings().first()
        except Exception as e:
            print(f"Error fetching single row: {e}")
            return None

    def fetch_all(self, query, params=None):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result.mappings().all()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def execute(self, query, params=None):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except Exception as e:
            print(f"Error executing query: {e}")
            return 0
