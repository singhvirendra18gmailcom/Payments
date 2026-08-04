ALTER TABLE document_chunks ADD COLUMN embedding_json TEXT;
ALTER TABLE document_chunks ADD COLUMN embedding_model VARCHAR;
ALTER TABLE document_chunks ADD COLUMN embedding_dimension INTEGER;
ALTER TABLE document_chunks ADD COLUMN embedding_status VARCHAR DEFAULT 'pending';
ALTER TABLE document_chunks ADD COLUMN embedding_error TEXT;
ALTER TABLE document_chunks ADD COLUMN embedded_at DATETIME;