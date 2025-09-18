import psycopg2


def connect_to_db(db_url):
    if not db_url:
        print("Error: DATABASE_URL environment variable not set.")
        return

    conn = None
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        print("Connection successful!")

        cursor = conn.cursor()

        print("Executing a test query...")
        cursor.execute("SELECT version();")

        db_version = cursor.fetchone()
        print(f"PostgreSQL database version: {db_version[0]}")

        cursor.close()

    except psycopg2.Error as e:
        print(f"Error connecting to or interacting with the database: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
