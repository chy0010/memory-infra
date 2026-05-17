-- Schema for Agent Memory project
-- Day 9: Added tsvector column for BM25-style keyword search (hybrid retrieval)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    tags TEXT[] DEFAULT '{}',
    source TEXT DEFAULT 'manual',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity searches (existing)
-- Tag filtering
CREATE INDEX IF NOT EXISTS idx_conversations_tags ON conversations USING GIN (tags);

-- Source filtering
CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations (source);

-- Full-text search (new)
CREATE INDEX IF NOT EXISTS idx_conversations_content_tsv ON conversations USING GIN (content_tsv);