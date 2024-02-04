CREATE TABLE
    embeddings (
    page_id UUID NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    page_url VARCHAR NOT NULL,
    page_title VARCHAR,
    embedding BYTEA NOT NULL,
    page_last_updated TIMESTAMP,
    embedding_last_updated TIMESTAMP,
    text_nonce BYTEA,
    text_encrypted BYTEA,
    parent_id UUID
);

ALTER TABLE embeddings
    ADD CONSTRAINT embeddings_pk PRIMARY KEY (page_id, user_id);

CREATE TABLE
    last_updates (
    user_id VARCHAR(64) NOT NULL PRIMARY KEY,
    last_update TIMESTAMP NOT NULL,
    finished SMALLINT
);

CREATE TABLE
    comparisons (
    comparison_id VARCHAR(32) NOT NULL
        CONSTRAINT comparisons_pk PRIMARY KEY,
    time_updated TIMESTAMP NOT NULL,
    comparison_nonce BYTEA NOT NULL,
    comparison_encrypted BYTEA NOT NULL
);

CREATE TABLE
    comparison_embeddings (
    comparison_id VARCHAR(32) NOT NULL
        CONSTRAINT comparison_embeddings_comparisons_comparison_id_fk REFERENCES public.comparisons,
    page_id VARCHAR NOT NULL,
    embedding VECTOR(1536),
    CONSTRAINT comparison_embeddings_pk PRIMARY KEY (comparison_id, page_id)
);

CREATE TABLE ideas (
    idea_id SERIAL
        CONSTRAINT ideas_pk PRIMARY KEY,
    cache_id VARCHAR(32) NOT NULL,
    time_updated TIMESTAMP NOT NULL,
    title_nonce BYTEA NOT NULL,
    title_encrypted BYTEA NOT NULL,
    description_nonce BYTEA NOT NULL,
    description_encrypted BYTEA NOT NULL
);

CREATE TABLE idea_embeddings (
    cache_id VARCHAR(32) NOT NULL,
    page_id VARCHAR NOT NULL,
    embedding VECTOR NOT NULL,
    CONSTRAINT idea_embeddings_pk
        PRIMARY KEY (cache_id, page_id)
);
