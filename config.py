from dotenv import load_dotenv
import os

load_dotenv()


SUBREDDITS = [
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

DB_URL = os.getenv("DATABASE_URL")
