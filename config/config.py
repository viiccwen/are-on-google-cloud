import os
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()


class Config:
    PROJECT_ID = os.getenv("PROJECT_ID", "")
    LOCATION = os.getenv("LOCATION", "us-central1")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "textembedding-gecko")
    DATASET_ID = os.getenv("DATASET_ID", "are_rag")
    TABLE_ID = os.getenv("TABLE_ID", "documents")
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "")
    API_KEY = os.getenv("API_KEY")

    def __init__(self):
        self.PROJECT_ID = os.getenv("PROJECT_ID")
        self.LOCATION = os.getenv("LOCATION")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME")
        self.CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
        self.DATASET_ID = os.getenv("DATASET_ID")
        self.TABLE_ID = os.getenv("TABLE_ID")
        self.API_KEY = os.getenv("API_KEY")

    @classmethod
    def get_bigquery_table(cls) -> str:
        return f"{cls.PROJECT_ID}.{cls.DATASET_ID}.{cls.TABLE_ID}"

    @classmethod
    def get_credentials(cls) -> service_account.Credentials:
        return service_account.Credentials.from_service_account_file(
            cls.CREDENTIALS_FILE
        )
