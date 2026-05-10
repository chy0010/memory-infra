-- Schema for Agent Memory project
-- Day 6: Added metadata columns for filtered retrieval

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    tags TEXT[] DEFAULT '{}',
    source TEXT DEFAULT 'manual',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for filtering by tags (GIN index works well for array contains queries)
CREATE INDEX IF NOT EXISTS idx_conversations_tags ON conversations USING GIN (tags);

-- Index for filtering by source
CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations (source);
