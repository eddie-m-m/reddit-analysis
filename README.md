# Sentiment Analysis of Data-Related Subreddits

This project is designed to analyze the perceived usefulness of various data-related
subreddits. It collects posts and comments, performs an initial sentiment analysis
using VADER to gauge community opinion, and then validates these findings using [**tbd**: DistilBERT or Logistic Regression]. The entire pipeline is built to be automated, with data stored in a PostgreSQL database and utilities for easy data export and backup.

---

## Features

- **Targeted Data Collection**: Idempotent scripts fetch posts and comments from data-related subreddits via `SUBREDDITS` list.
- **Automated Pipeline**: Data collection can be scheduled with cron jobs for continuous analysis.
- **Two-Stage Sentiment Analysis**: Uses VADER for fast, initial sentiment scoring.
- **Model Validation**: Includes a planned validation step to compare VADER's results against predictions from a [**tbd**: DistilBERT or Logistic Regression] for enhanced accuracy.
- **Structured Data Storage**: Utilizes a PostgreSQL database managed via Docker.
- **Flexible Data Export**: Export tables into both `.csv` and `.parquet` formats for analysis in other tools.
- **Robust Utilities**: Includes scripts for database backups, cron job management, and comprehensive logging.

---
