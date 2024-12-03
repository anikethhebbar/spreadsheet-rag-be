from fastapi import APIRouter, HTTPException
from ..schemas.query_schema import QueryRequest, QueryResponse
from ..services.query_service import QueryService

router = APIRouter()
query_service = QueryService()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query"""
    try:
        result = await query_service.process_query(
            request.query,
            use_history=request.chat_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 