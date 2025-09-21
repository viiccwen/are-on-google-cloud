from google.cloud import bigquery
import vertexai
import pandas as pd
from vertexai.language_models import TextEmbeddingModel
from config.config import Config

vertexai.init(
    project=Config.PROJECT_ID,
    location=Config.LOCATION,
    credentials=Config.get_credentials(),
)
bq = bigquery.Client(project=Config.PROJECT_ID, credentials=Config.get_credentials())
embed_model = TextEmbeddingModel.from_pretrained(Config.EMBED_MODEL_NAME)


def retrieve(query: str, top_k: int = 5) -> pd.DataFrame:
    query_embedding = embed_model.get_embeddings([query])[0].values
    sql = f"""
    SELECT 
        doc_id, 
        title, 
        content, 
        ML.DISTANCE(embedding, @query_embedding, 'COSINE') AS distance
    FROM `{Config.get_bigquery_table()}`
    ORDER BY distance ASC
    LIMIT {top_k}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding)
        ]
    )
    return bq.query(sql, job_config=job_config).result().to_dataframe()


def main():
    query = "什麼是 Python Decorator?"
    df = retrieve(query)
    print(df[["distance", "title", "content"]])


if __name__ == "__main__":
    main()
