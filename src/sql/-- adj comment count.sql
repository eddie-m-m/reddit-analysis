-- adj comment count
-- all subreddits minus r/dataisbeautiful
SELECT COUNT(*) AS total_comment_count
FROM comments;
SELECT COUNT(*) as without_data_is_beautiful
FROM comments c
    JOIN posts p ON c.post_id = p.post_id
WHERE p.subreddit_id != 1;