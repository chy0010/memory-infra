"""
store.py - Day 6: Store a conversation with embedding and metadata.

Usage:
    python store.py "text here"
    python store.py "text here" --tags work,python --source manual
"""

import os
import sys
import json
import argparse
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
db_url = os.getenv("DATABASE_URL")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Store a conversation with its embedding")
parser.add_argument("text", nargs="+", help="The conversation text to store")
parser.add_argument("--tags", default="", help="Comma-separated tags (e.g., work,python)")
parser.add_argument("--source", default="manual", help="Source of the conversation")

args = parser.parse_args()

# Process the inputs
text = " ".join(args.text)
tags = [t.strip() for t in args.tags.split(",") if t.strip()]
source = args.source
metadata = {}  # Empty for now, can be extended later

# Get the embedding from OpenAI
print(f"Getting embedding for: {text}")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)
embedding = response.data[0].embedding
print(f"Got embedding of {len(embedding)} dimensions")

# Insert into Postgres
print("Connecting to Postgres...")
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO conversations (content, embedding, tags, source, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (text, str(embedding), tags, source, json.dumps(metadata))
        )
        new_id = cur.fetchone()[0]
        conn.commit()

print(f"Stored conversation with id={new_id}")
print(f"  tags: {tags}")
print(f"  source: {source}")