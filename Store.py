"""
store.py - Day 4-5: Store a conversation with its embedding in Postgres.
Takes the text to store as a command-line argument.
"""

import os
import sys
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
db_url = os.getenv("DATABASE_URL")

# Get the text from command line, or use a default
if len(sys.argv) > 1:
    text = " ".join(sys.argv[1:])
else:
    text = "I am learning to build memory infrastructure for AI agents."

print(f"Getting embedding for: {text}")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)
embedding = response.data[0].embedding
print(f"Got embedding of {len(embedding)} dimensions")

print("Connecting to Postgres...")
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO conversations (content, embedding) VALUES (%s, %s) RETURNING id",
            (text, str(embedding))
        )
        new_id = cur.fetchone()[0]
        conn.commit()

print(f"Stored conversation with id={new_id}")