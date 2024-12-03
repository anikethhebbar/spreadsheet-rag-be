from fastapi import APIRouter, Depends
import google.generativeai as genai
from config import Settings
from schemas.query_schema import QueryRequest, QueryResponse

router = APIRouter()

def get_settings():
    return Settings()

@router.post("/query", response_model=QueryResponse)
async def process_query(query: QueryRequest, settings: Settings = Depends(get_settings)):
    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # Your existing Gemini logic here
    model = genai.GenerativeModel('gemini-pro')
    # ... rest of your code 