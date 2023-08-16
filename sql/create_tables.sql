create table embeddings (
    page_id uuid not null,
    user_id varchar(64) not null,
    page_url varchar not null,
    page_title varchar,
    embedding bytea not null,
    page_last_updated timestamp,
    embedding_last_updated timestamp,
    text_nonce bytea,
    text_encrypted bytea,
    parent_id uuid
);

alter table embeddings
    add constraint embeddings_pk
        primary key (page_id, user_id);

create table last_updates (
    user_id varchar(64) not null primary key,
    last_update timestamp not null,
    finished smallint
);
