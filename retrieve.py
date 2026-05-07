"""
retrieve.py - Day 5: Find the most similar past conversations to a query.
Takes a query as a command-line argument, returns the top 5 closest matches.
"""

import os
import sys
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
db_url = os.getenv("DATABASE_URL")

# Get the query from command line, or use a default
if len(sys.argv) > 1:
    query = " ".join(sys.argv[1:])
else:
    query = "programming and software"

print(f"Query: {query}")

# Step 1: Embed the query the same way we embedded the stored conversations
print("Embedding the query...")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = response.data[0].embedding

# Step 2: Search Postgres for the closest matches
print("Searching for similar conversations...\n")
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        DISTANCE_THRESHOLD = 0.7
        
        cur.execute(
            """
            SELECT id, content, embedding <=> %s::vector AS distance
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
    print(f"No good matches found (all results above distance threshold of {DISTANCE_THRESHOLD}).")
    print("Try a different query or add more conversations to the database.")
else:
    print(f"Top {len(results)} most similar conversations (threshold: {DISTANCE_THRESHOLD}):\n")
    for rank, (row_id, content, distance) in enumerate(results, start=1):
        print(f"{rank}. [id={row_id}] (distance={distance:.4f})")
        print(f"   {content}\n")