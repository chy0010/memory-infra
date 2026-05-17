# memory-infra

Memory infrastructure for AI agents.

## What this is

I'm building a memory system that lets AI agents remember things across conversations — persistently, accurately, and efficiently.

Most AI applications today have no real memory. Each conversation starts from scratch, or they bolt on a basic vector search and call it "RAG." That's not enough for agents that need to remember context, learn from past interactions, and reason over time.

This project explores what real memory infrastructure for agents should look like.

## What I'm building

A memory system with three layers:

- **Working memory** — the current conversation context
- **Episodic memory** — past conversations, retrievable by similarity and metadata
- **Semantic memory** — extracted facts and entities, stored in a knowledge graph

On top of that:

- Hybrid retrieval (vector + keyword + graph)
- Agentic retrieval — the agent decides what to fetch and when
- A real evaluation harness measuring recall, groundedness, latency, and cost
- Continuous re-embedding when models change

## Why

The companies building serious AI products — Anthropic, OpenAI, Google, the AI startups — are all solving memory and retrieval internally, often badly. It's one of the most important and least-solved problems in AI engineering today.

I'm a data engineer learning AI infrastructure in public. This project is how I'm going deep.

## Status

Day 1. Starting from the dumbest possible version and building up.

Follow the journey: [[LinkedIn](#)](https://www.linkedin.com/in/krishna-profile-link/?skipRedirect=true) | [[Twitter](#)](https://x.com/Chaikrishnan)

## Stack

- Python
- Postgres + pgvector
- OpenAI embeddings (will swap to open-source later)
- Claude / OpenAI APIs for the agent layer
- Neo4j or Kuzu for the knowledge graph (later phase)


## License

MIT
