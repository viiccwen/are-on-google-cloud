from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Query request model"""

    query: str = Field(..., description="Query text", min_length=1, max_length=1000)
    top_k: int = Field(default=5, description="Number of documents to return", ge=1, le=20)


class DocumentChunk(BaseModel):
    """Document chunk model"""

    doc_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    distance: float = Field(..., description="Similarity distance")
    chunk_index: Optional[int] = Field(None, description="Chunk index")
    total_chunks: Optional[int] = Field(None, description="Total number of chunks")


class QueryResponse(BaseModel):
    """Query response model"""

    query: str = Field(..., description="Original query")
    documents: List[DocumentChunk] = Field(..., description="List of relevant documents")
    total_found: int = Field(..., description="Total number of documents found")
    success: bool = Field(default=True, description="Whether the query was successful")
    message: Optional[str] = Field(None, description="Response message")


class IndexRequest(BaseModel):
    """Index request model"""

    limit: int = Field(default=100, description="Number of documents to index", ge=1, le=1000)


class IndexResponse(BaseModel):
    """Index response model"""

    success: bool = Field(..., description="Whether indexing was successful")
    message: str = Field(..., description="Response message")
    documents_processed: int = Field(..., description="Number of documents processed")
    chunks_created: int = Field(..., description="Number of chunks created")
