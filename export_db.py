import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

tables_to_export = ["subreddits", "authors", "posts", "comments", "sentiment_analysis"]

CSV_DIR = "csv_exports"
PARQUET_DIR = "parquet_exports"


def create_directories():
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(PARQUET_DIR, exist_ok=True)
    print(f"Created directories: '{CSV_DIR}/' and '{PARQUET_DIR}/'")


def export_postgres_to_csv():
    print("\n--- Starting PostgreSQL to CSV Export ---")
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                for table_name in tables_to_export:
                    csv_filepath = os.path.join(CSV_DIR, f"{table_name}.csv")
                    print(f"Exporting table '{table_name}' to '{csv_filepath}'...")

                    sql_query = f"COPY {table_name} TO STDOUT WITH CSV HEADER"

                    with open(csv_filepath, "w", encoding="utf-8") as f:
                        cursor.copy_expert(sql_query, f)

                    print(f"Successfully exported '{table_name}'.")

    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        print("Please check your .env file and ensure PostgreSQL is running.")
    except Exception as e:
        print(f"An unexpected error occurred during CSV export: {e}")


def convert_csv_to_parquet():
    print("\n--- Starting CSV to Parquet Conversion ---")
    try:
        for table_name in tables_to_export:
            csv_filepath = os.path.join(CSV_DIR, f"{table_name}.csv")
            parquet_filepath = os.path.join(PARQUET_DIR, f"{table_name}.parquet")

            if os.path.exists(csv_filepath):
                print(f"Converting '{csv_filepath}' to '{parquet_filepath}'...")

                df = pd.read_csv(csv_filepath)

                df.to_parquet(parquet_filepath, index=False)

                print(f"Successfully converted '{table_name}' to Parquet.")
            else:
                print(
                    f"Warning: CSV file for table '{table_name}' not found. Skipping."
                )

    except Exception as e:
        print(f"An error occurred during Parquet conversion: {e}")


print("--- ETL SCRIPT: PostgreSQL to Parquet ---")
create_directories()
export_postgres_to_csv()
convert_csv_to_parquet()
print("\n--- ETL Process Finished ---")
