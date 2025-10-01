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
    "deeplearning",
    "rstats",
    "PowerBI",
    "tableau",
    "Looker",
    "LookerStudio",
    "bigdata",
    "analytics",
    "analyticsengineering",
    "LanguageTechnology",
    "excel",
    "MicrosoftExcel",
    "googlesheets",
    "learnmachinelearning",
    "businessanalyst",
]

DB_URL = os.getenv("DATABASE_URL")
