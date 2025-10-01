-- posts info
SELECT subreddit_id,
    COUNT(*) FILTER (
        WHERE author_fullname IS NULL
    ) AS null_author_count,
    COUNT(*) AS total_post_count
FROM posts p
GROUP BY subreddit_id
ORDER BY subreddit_id;
SELECT COUNT(*) AS total_post_count
FROM posts;