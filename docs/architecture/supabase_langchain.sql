-- Supabase + LangChain SupabaseVectorStore 기본 스키마 템플릿
-- 임베딩 차원: OpenAI text-embedding-3-small → 1536
-- HuggingFace all-MiniLM-L6-v2 → 384 (테이블·함수의 vector(N)을 함께 변경)
--
-- 팀 Supabase 프로젝트 SQL 에디터에서 실행 후 service_role 키를 백엔드 환경변수로만 사용.

create extension if not exists vector;

create table if not exists documents (
  id text primary key,
  content text,
  metadata jsonb default '{}'::jsonb,
  embedding vector(1536)
);

create index if not exists documents_embedding_idx
  on documents
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- LangChain match_args: query_embedding + 선택적 filter (jsonb)
create or replace function match_documents(
  query_embedding vector(1536),
  filter jsonb default null
)
returns table (
  id text,
  content text,
  metadata jsonb,
  similarity float8
)
language sql
stable
as $$
  select
    d.id,
    d.content,
    d.metadata,
    1 - (d.embedding <=> query_embedding) as similarity
  from documents d
  where
    filter is null
    or filter = '{}'::jsonb
    or d.metadata @> filter
  order by d.embedding <=> query_embedding;
$$;
