-- comment info
SELECT COUNT(*) AS total_comment_count
FROM comments;
SELECT p.subreddit_id,
    COUNT(*) FILTER (
        WHERE c.author_fullname IS NULL
    ) AS null_author_count,
    COUNT(*) FILTER (
        WHERE c.body = '[deleted]'
    ) AS deleted_comment_count,
    COUNT(*) FILTER (
        WHERE c.author_fullname IS NULL
            AND body = '[deleted]'
    ) AS both_conditions_true_count,
    COUNT(c.*) AS total_comment_count
FROM comments c
    JOIN posts p ON c.post_id = p.post_id
GROUP BY p.subreddit_id
ORDER BY p.subreddit_id;