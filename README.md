# Sentiment Analysis of Data-Related Subreddits

This project is designed to analyze the perceived usefulness of various data-related
subreddits. It collects posts and comments, performs an initial sentiment analysis
using VADER to gauge community opinion, and then validates these findings using a classical Logistic Regression. The entire pipeline is built to be automated, with data mangaged and stored in a containerized PostgreSQL and utilities for easy data export and backup.

---

## Project Features

- **Automated Data Collection**: Idempotent scripts fetch posts and comments from data-related subreddits and can be scheduled with cron jobs.
- **Sentiment Analysis**: Uses VADER for fast, initial sentiment scoring.
- **Model Validation**: Includes a validation step to compare VADER's results against predictions from a classical Logistic Regression for enhanced accuracy.
- **Utilities**: Scripts cover cron job management, comprehensive logging, database backups and exports.

---

## What is Analyzed? How the findings are found

How useful do people find subreddits related to topics of "data"? We answer this by constructing a `Usefulness Index`. The Usefulness Index is derived from the following four metrics:

- _Average Compound Score_ ($\bar C$) : the mean of all compound scores per subreddit.

- _Sentiment-Weighted Engagement_ (SWE): $\frac{1}{N}\sum_{i=1}^{N} C_{i} \times log(MAX(0,score_{i}) + 1))$
- _Constructive Ratio_ (CR): $\frac{number \space of\space positive}{number\space of\space negative\space +\space 1}$.

  "Positive" is a `vader_compound` score `>= 0.05`. "Negative" is a `vader_compound` score `<= -0.05`.

- _Information Density_ (ID): the mean of ($neutral_{i} \times log(word\_count_{i} + 1$)).

  `Usefulness Index` = $(w_1 \times Norm(\bar C)) + (w_2 \times Norm(SWE)) + (w_3 \times Norm(CR)) + (w_4 \times Norm(ID))$

where normalization was done through min-max scaling.

Weight choices:

## Intuition and assumptions

- _Average Compount Score_: Overall vibe check of a subreddit. Assumes the overall average sentiment roughly gauges how it is received by the community (e.g. higher scores mean more positivity, more helpfulness, etc.).
- _Sentiment-weighted Engagement_: Measures community feedback on positive comments. Assumes that the more popular (i.e. upvoted) that positive comments are, the more "helpful" they are.
- _Constructive Ratio_: Considers "health" of the discussion. Assumes that the more positive comments there are relative to negative comments, the healthier and more constructive the subreddit is.
- _Information Density_: Rewards comments that are longer and more neutral. Assumes this may mean more "substance" in the comment.

## Validation

The steps taken for validation were:

1. 1,000 randomly sampled comments were manually labeled (ground truth)
2.
3.
