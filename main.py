from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

from schemas.rag import QueryRequest, IndexRequest, IndexResponse
from schemas.tools import AvailableToolsResponse
from schemas.function_calling import FunctionCallRequest
from schemas.common import ErrorResponse, HealthResponse, SuccessResponse
from schemas.response import FunctionCallResponse, RAGResponse

from agent.retriever import retrieve
from agent.indexer import main as index_main
from agent.tools import get_available_tools
from agent.function_caller import function_caller
from telemetry.manager import telemetry

app = FastAPI(
    title="ARE RAG API",
    description="基於 BigQuery 和 Vertex AI 的 RAG API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=f"內部服務器錯誤: {str(exc)}", error_code="INTERNAL_SERVER_ERROR"
        ).dict(),
    )


@app.get("/", response_model=SuccessResponse)
async def root():
    """Root endpoint"""
    return SuccessResponse(
        message="歡迎使用 ARE RAG API",
        data={"docs": "/docs", "health": "/health", "version": "1.0.0"},
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        services={"bigquery": "connected", "vertex_ai": "connected", "api": "running"},
    )


# ===== RAG =====
@app.post("/query", response_model=RAGResponse)
async def query_documents(request: QueryRequest, user_id: str = "anonymous"):
    """Query relevant documents"""
    try:

        @telemetry.track_rag_query(user_id=user_id)
        def _query_with_telemetry(query: str, top_k: int):
            results_df = retrieve(query, top_k)
            documents = []
            for _, row in results_df.iterrows():
                documents.append(
                    {
                        "doc_id": row["doc_id"],
                        "title": row["title"],
                        "content": row["content"],
                        "distance": float(row["distance"]),
                    }
                )
            return {"documents": documents, "total_found": len(documents)}

        result = _query_with_telemetry(request.query, request.top_k)

        return RAGResponse(
            message=f"找到 {result['total_found']} 個相關文檔",
            success=True,
            documents_count=result["total_found"],
        )

    except Exception as e:
        telemetry.logger.log_error(
            e, {"operation": "rag_query", "query": request.query}, user_id
        )
        raise HTTPException(status_code=500, detail="查詢失敗，請稍後再試")


@app.post("/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest):
    """Index documents"""
    try:
        index_main()

        return IndexResponse(
            success=True,
            message="文檔索引建立成功",
            documents_processed=request.limit,
            chunks_created=request.limit,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引建立失敗: {str(e)}")


# ===== Tools =====
@app.get("/tools", response_model=AvailableToolsResponse)
async def get_tools():
    """Get all available tools list"""
    tools = get_available_tools()
    return AvailableToolsResponse(tools=tools, total_count=len(tools))


@app.post("/tools/chat", response_model=FunctionCallResponse)
async def chat_with_tools(request: FunctionCallRequest, user_id: str = "anonymous"):
    """Natural language tool calling"""
    try:

        @telemetry.track_function_call("chat_with_tools", user_id=user_id)
        def _chat_with_telemetry(message: str):
            return function_caller.process_message(message)

        result = _chat_with_telemetry(request.message)

        telemetry.log_user_interaction(
            user_id=user_id,
            action="tool_chat",
            details={
                "message": request.message,
                "function_calls_count": len(result.get("function_calls", [])),
            },
        )

        return FunctionCallResponse(
            message=result.get("response", "處理完成"),
            success=result.get("success", True),
        )

    except Exception as e:
        telemetry.logger.log_error(
            e, {"operation": "tool_chat", "message": request.message}, user_id
        )
        return FunctionCallResponse(
            message="抱歉，處理您的請求時發生錯誤，請稍後再試。", success=False
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
