import praw
import pandas as pd


def get_posts_praw(conn, reddit: praw.Reddit, subreddits: list):
    for subreddit in subreddits:
        print(f"--- Starting subreddit: r/{subreddit} ---")

        try:
            subreddit = reddit.subreddit(subreddit)
            top_posts = subreddit.top(time_filter="year", limit=1000)

            posts_data = []
            for post in top_posts:
                posts_data.append(
                    {
                        "post_id": post.id,
                        "subreddit": post.subreddit.display_name,
                        "title": post.title,
                        "author": post.author.name if post.author else "[deleted]",
                        "created_utc": pd.to_datetime(post.created_utc, unit="s"),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "url": post.url,
                        "selftext": post.selftext,
                    }
                )

            if not posts_data:
                print(f"No posts found for r/{subreddit}. Skipping.")
                continue

            df = pd.DataFrame(posts_data)

            df.to_sql("posts", conn, if_exists="append", index=False)
            print(
                f"Successfully saved {len(df)} posts for r/{subreddit} to the database."
            )

        except Exception as e:
            print(f"An error occurred for subreddit r/{subreddit}: {e}")
