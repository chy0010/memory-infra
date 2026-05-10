"""
retrieve.py - Day 6: Find similar past conversations with optional tag filtering.

Usage:
    python retrieve.py "your query"
    python retrieve.py "your query" --tags work
    python retrieve.py "your query" --tags work,deployment
"""

import os
import argparse
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
db_url = os.getenv("DATABASE_URL")

# Threshold can be set via environment variable, otherwise defaults to 0.7
DISTANCE_THRESHOLD = float(os.getenv("DISTANCE_THRESHOLD", "0.85"))

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Find similar past conversations")
parser.add_argument("query", help="The query text (wrap in quotes if it has spaces)")
parser.add_argument("--tags", default="", help="Filter by tags (comma-separated)")

args = parser.parse_args()

query = args.query
filter_tags = [t.strip() for t in args.tags.split(",") if t.strip()]

print(f"Query: {query}")
if filter_tags:
    print(f"Filtering by tags: {filter_tags}")

# Step 1: Embed the query
print("Embedding the query...")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = response.data[0].embedding

# Step 2: Search Postgres with optional tag filtering
print("Searching for similar conversations...\n")
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        if filter_tags:
            # Filter by tags AND distance threshold
            cur.execute(
                """
                SELECT id, content, tags, embedding <=> %s::vector AS distance
                FROM conversations
                WHERE embedding <=> %s::vector < %s
                  AND tags && %s
                ORDER BY distance
                LIMIT 5
                """,
                (str(query_embedding), str(query_embedding), DISTANCE_THRESHOLD, filter_tags)
            )
        else:
            # Just filter by distance threshold
            cur.execute(
                """
                SELECT id, content, tags, embedding <=> %s::vector AS distance
                FROM conversations
                WHERE embedding <=> %s::vector < %s
                ORDER BY distance
                LIMIT 5
                """,
                (str(query_embedding), str(query_embedding), DISTANCE_THRESHOLD)
            )
        results = cur.fetchall()

# Step 3: Print results
if not results:
    print(f"No good matches found (threshold: {DISTANCE_THRESHOLD}).")
    if filter_tags:
        print(f"Tried filtering by tags: {filter_tags}")
    print("Try a different query, different tags, or add more conversations.")
else:
    print(f"Top {len(results)} most similar conversations (threshold: {DISTANCE_THRESHOLD}):\n")
    for rank, (row_id, content, tags, distance) in enumerate(results, start=1):
        print(f"{rank}. [id={row_id}] (distance={distance:.4f}) tags={tags}")
        print(f"   {content}\n")