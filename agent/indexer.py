from typing import List
import pandas as pd
import vertexai
from config.config import Config
from google.cloud import bigquery
from google.cloud.bigquery_storage import BigQueryReadClient
from vertexai.language_models import TextEmbeddingModel

vertexai.init(
    project=Config.PROJECT_ID,
    location=Config.LOCATION,
    credentials=Config.get_credentials(),
)

bq = bigquery.Client(project=Config.PROJECT_ID, credentials=Config.get_credentials())
embed_model = TextEmbeddingModel.from_pretrained(Config.EMBED_MODEL_NAME)

MAX_CHARS = 2000


def chunk_text(text: str, chunk_size: int = MAX_CHARS, overlap: int = 200) -> List[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            period_pos = text.rfind(".", start, end)
            space_pos = text.rfind(" ", start, end)

            if period_pos > start and period_pos > space_pos:
                end = period_pos + 1
            elif space_pos > start:
                end = space_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start >= len(text):
            break

    return chunks


def load_data(limit: int = 100) -> pd.DataFrame:
    sql = f"""
    SELECT id, title, body
    FROM `bigquery-public-data.stackoverflow.posts_questions`
    WHERE tags LIKE '%python%'
    LIMIT {limit}
    """
    bqstorage = BigQueryReadClient(credentials=Config.get_credentials())
    return bq.query(sql).result().to_dataframe(bqstorage)


def embed_data(data: pd.DataFrame) -> pd.DataFrame:
    all_chunks = []
    all_embeddings = []
    all_metadata = []

    for idx, row in data.iterrows():
        chunks = chunk_text(str(row["body"]), chunk_size=MAX_CHARS, overlap=200)
        embeddings = embed_model.get_embeddings(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            all_chunks.append(chunk)
            all_embeddings.append(embedding.values)
            all_metadata.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
            )

    result_data = pd.DataFrame(all_metadata)
    result_data["body"] = all_chunks
    result_data["embedding"] = all_embeddings

    return result_data


def index_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.rename(columns={"id": "doc_id", "body": "content"})[
        ["doc_id", "title", "content", "embedding"]
    ]
    df["doc_id"] = df["doc_id"].astype(str)

    table_id = Config.get_bigquery_table()
    job = bq.load_table_from_dataframe(df, table_id)
    job.result()
    print(f"[INFO] Data indexed successfully - {len(df)} chunks processed")


def main():
    data = load_data()
    # print(data.head())
    data = embed_data(data)
    data = index_data(data)
    # print(data)


if __name__ == "__main__":
    main()
