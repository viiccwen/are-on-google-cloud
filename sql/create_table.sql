CREATE SCHEMA IF NOT EXISTS `are_rag`;

CREATE OR REPLACE TABLE `are_rag.documents` (
  doc_id STRING,
  title STRING,
  content STRING,
  embedding ARRAY<FLOAT64>
);