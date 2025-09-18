import praw
import pandas as pd


def get_comments_praw(conn, reddit: praw.Reddit, subreddits: list):
    for subreddit in subreddits:
        print(f"--- Starting comments for subreddit: r/{subreddit} ---")

        try:
            post_ids_df = pd.read_sql(
                f"SELECT post_id FROM posts WHERE subreddit = '{subreddit}'", conn
            )
            post_ids = post_ids_df["post_id"].tolist()
        except Exception as e:
            print(f"Could not fetch post_ids for r/{subreddit}: {e}")
            continue

        if not post_ids:
            print(f"No posts found in database for r/{subreddit}. Skipping.")
            continue

        print(f"Found {len(post_ids)} posts for r/{subreddit}. Fetching comments...")
        all_comments_data = []

        for idx, post_id in enumerate(post_ids):
            try:
                submission = reddit.submission(id=post_id)
                submission.comment_sort = "top"

                # This line processes "MoreComments" objects, replacing them with actual comments.
                # limit=5 means we'll expand the top 5 "more" links. Use limit=None to expand all.
                # Use limit=0 to just remove them without fetching more comments.
                submission.comments.replace_more(limit=5)

                for comment in submission.comments.list():
                    all_comments_data.append(
                        {
                            "comment_id": comment.id,
                            "post_id": comment.submission.id,
                            "author": comment.author.name
                            if comment.author
                            else "[deleted]",
                            "created_utc": pd.to_datetime(
                                comment.created_utc, unit="s"
                            ),
                            "score": comment.score,
                            "body": comment.body,
                        }
                    )

                if (idx + 1) % 25 == 0:
                    print(f"  Processed {idx + 1}/{len(post_ids)} posts...")

            except Exception as e:
                print(f"  Error processing comments for post {post_id}: {e}")

        if not all_comments_data:
            print(f"No comments collected for r/{subreddit}. Skipping.")
            continue

        df = pd.DataFrame(all_comments_data)

        df.to_sql("comments", conn, if_exists="append", index=False)
        print(
            f"Successfully saved {len(df)} comments for r/{subreddit} to the database."
        )
