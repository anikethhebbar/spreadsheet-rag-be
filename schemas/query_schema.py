from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[bool] = False  # Whether to use chat history, if needed

class QueryResponse(BaseModel):
    query: str
    sql_query: Optional[str] = None
    results: Optional[List[Dict[Any, Any]]] = None
    answer: str
    used_history: bool = False 