-- schema.sql
DROP TABLE IF EXISTS sentiment_analysis;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS subreddits;
-- subreddits: the subreddits
CREATE TABLE subreddits (
    subreddit_id SERIAL PRIMARY KEY,
    subreddit VARCHAR(255) UNIQUE NOT NULL,
    member_count INTEGER,
    member_count_date TIMESTAMP,
    collection_date TIMESTAMP
);
-- authors: author names and unique reddit ids
CREATE TABLE authors (
    author_fullname VARCHAR(25) PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL
);
-- posts: all collected posts from the subreddits
CREATE TABLE posts (
    post_id VARCHAR(20) PRIMARY KEY,
    subreddit_id INTEGER NOT NULL REFERENCES subreddits(subreddit_id) ON DELETE CASCADE,
    author_fullname VARCHAR(25) REFERENCES authors(author_fullname),
    title TEXT NOT NULL,
    selftext TEXT,
    created_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    url TEXT,
    flair VARCHAR(255),
    score INTEGER,
    num_comments INTEGER,
    upvote_ratio REAL,
    stickied BOOLEAN
);
-- comments: individual comments
CREATE TABLE comments (
    comment_id VARCHAR(20) PRIMARY KEY,
    post_id VARCHAR(20) NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    author_fullname VARCHAR(25) REFERENCES authors(author_fullname),
    parent_id VARCHAR(20),
    body TEXT NOT NULL,
    created_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    score INTEGER,
    depth INTEGER,
    is_submitter BOOLEAN,
    stickied BOOLEAN
);
-- sentiment_analysis: the sentiment scores for each comment
CREATE TABLE sentiment_analysis (
    analysis_id SERIAL PRIMARY KEY,
    comment_id VARCHAR(20) NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
    cleaned_body TEXT,
    vader_compound FLOAT,
    vader_positive FLOAT,
    vader_negative FLOAT,
    vader_neutral FLOAT,
    word_count INTEGER,
    UNIQUE(comment_id)
);
CREATE INDEX idx_posts_subreddit_id ON posts(subreddit_id);
CREATE INDEX idx_posts_author_fullname ON posts(author_fullname);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_fullname ON comments(author_fullname);
CREATE INDEX idx_sentiment_analysis_comment_id ON sentiment_analysis(comment_id);
-- for reconstructing comment threads
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
-- for time-series analysis
CREATE INDEX idx_posts_created_utc ON posts(created_utc);