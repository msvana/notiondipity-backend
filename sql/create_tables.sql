create table embeddings (
    page_id uuid not null primary key,
    user_id uuid not null,
    page_url varchar not null,
    page_title varchar,
    embedding bytea not null,
    page_last_updated timestamp,
    embedding_last_updated timestamp
);

create table last_updates (
    user_id uuid not null primary key,
    last_update timestamp not null,
    finished smallint
);
