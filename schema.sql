-- schema.sql

DROP TABLE IF EXISTS sentiment_analysis;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS subreddits;

-- subreddits: Stores the subreddits you are analyzing.
CREATE TABLE subreddits (
    subreddit_id    SERIAL PRIMARY KEY,
    subreddit_name  VARCHAR(255) UNIQUE NOT NULL,
    collection_date TIMESTAMP
);

-- posts: Stores all collected posts from the subreddits.
CREATE TABLE posts (
    post_id         VARCHAR(10) PRIMARY KEY,
    subreddit_id    INTEGER NOT NULL REFERENCES subreddits(subreddit_id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    flair           VARCHAR(255),
    selftext        TEXT,
    url             TEXT,
    author          VARCHAR(255),
    created_utc     TIMESTAMP NOT NULL,
    score           INTEGER,
    num_comments    INTEGER
);

-- comments: Stores individual comments for sentiment analysis.
CREATE TABLE comments (
    comment_id      VARCHAR(10) PRIMARY KEY,
    post_id         VARCHAR(10) NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    parent_id       VARCHAR(10),
    body            TEXT NOT NULL,
    author          VARCHAR(255),
    created_utc     TIMESTAMP NOT NULL,
    score           INTEGER
);

-- sentiment_analysis: Stores the sentiment scores for each comment.
CREATE TABLE sentiment_analysis (
    analysis_id     SERIAL PRIMARY KEY,
    comment_id      VARCHAR(10) NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
    cleaned_body    TEXT,
    vader_compound  FLOAT,
    vader_positive  FLOAT,
    vader_negative  FLOAT,
    vader_neutral   FLOAT,
    UNIQUE(comment_id) 
);

CREATE INDEX ON posts(subreddit_id);
CREATE INDEX ON comments(post_id);
CREATE INDEX ON sentiment_analysis(comment_id);