create table
  embeddings (
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

alter table embeddings add constraint embeddings_pk primary key (page_id, user_id);

create table
  last_updates (
    user_id varchar(64) not null primary key,
    last_update timestamp not null,
    finished smallint
  );

create table
  comparisons (
    comparison_id varchar(32) not null constraint comparisons_pk primary key,
    time_updated timestamp not null,
    comparison_nonce bytea not null,
    comparison_encrypted bytea not null
  );

create table
  comparison_embeddings (
    comparison_id varchar(32) not null constraint comparison_embeddings_comparisons_comparison_id_fk references public.comparisons,
    page_id varchar not null,
    embedding vector (1536),
    constraint comparison_embeddings_pk primary key (comparison_id, page_id)
  );

create table
  ideas (
    idea_id varchar(32) not null constraint ideas_pk primary key,
    time_updated timestamp not null,
    title_nonce bytea not null,
    title_encrypted bytea not null,
    description_nonce bytea not null,
    description_encrypted bytea not null
  );

create table
  idea_embeddings (
    idea_id varchar(32) not null constraint comparison_embeddings_comparisons_comparison_id_fk references public.comparisons,
    page_id varchar not null,
    embedding vector (1536),
    constraint idea_embeddings_pk primary key (idea_id, page_id)
  );
