"""
ingest.py - Day 6 (caught up on Day 7): Bulk ingest Hacker News stories into the database.

Fetches top stories from HN API, embeds them, stores them with metadata.

Usage:
    python ingest.py            # ingests 50 stories (default)
    python ingest.py --count 200    # ingests 200 stories
"""

import os
import time
import json
import argparse
import requests
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
db_url = os.getenv("DATABASE_URL")

# Parse arguments
parser = argparse.ArgumentParser(description="Ingest Hacker News stories")
parser.add_argument("--count", type=int, default=50, help="Number of stories to ingest")
args = parser.parse_args()

# Step 1: Fetch top story IDs from HN
print("Fetching top story IDs from Hacker News...")
top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
response = requests.get(top_stories_url)
story_ids = response.json()[:args.count]
print(f"Got {len(story_ids)} story IDs.\n")

# Step 2: For each story, fetch details, embed, and store
inserted = 0
skipped = 0
errors = 0

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for i, story_id in enumerate(story_ids, start=1):
            try:
                # Fetch story details
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story = requests.get(story_url).json()

                # Skip stories without titles
                if not story or not story.get("title"):
                    skipped += 1
                    continue

                title = story["title"]
                hn_url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                score = story.get("score", 0)
                author = story.get("by", "unknown")

                # Get embedding from OpenAI
                emb_response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=title
                )
                embedding = emb_response.data[0].embedding

                # Build metadata
                metadata = {
                    "hn_id": story_id,
                    "url": hn_url,
                    "score": score,
                    "author": author
                }

                # Insert into database
                cur.execute(
                    """
                    INSERT INTO conversations (content, embedding, tags, source, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (title, str(embedding), ['hackernews'], 'hn-import', json.dumps(metadata))
                )
                inserted += 1

                # Print progress every 10 stories
                if i % 10 == 0:
                    conn.commit()
                    print(f"  [{i}/{len(story_ids)}] Inserted {inserted} so far...")

            except Exception as e:
                errors += 1
                print(f"  Error on story {story_id}: {e}")

        conn.commit()

print(f"\nDone. Inserted: {inserted}, Skipped: {skipped}, Errors: {errors}")