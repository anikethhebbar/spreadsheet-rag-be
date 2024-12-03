from ..services.csv_service import DataService
from ..services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self):
        self.data_service = DataService()
        self.gemini_service = GeminiService()

    async def process_query(self, query: str, use_history: bool = False) -> dict:
        """Process a query using SQL and RAG"""
        logger.info(f"Processing query: {query}")
        
        # Get schema
        schema = self.data_service.get_schema()
        logger.info(f"Got schema: {schema}")
        
        # Try to generate and execute SQL
        sql_query = await self.gemini_service.process_query(
            query, 
            schema,
            use_history
        )
        logger.info(f"Generated SQL query: {sql_query}")
        
        results = None
        if sql_query:
            try:
                results = self.data_service.execute_query(sql_query)
                logger.info(f"Query results: {results}")
            except Exception as e:
                logger.error(f"Error executing query: {str(e)}")
                results = None
        
        # Generate explanation
        answer = await self.gemini_service.generate_explanation(
            query,
            sql_query,
            results,
            use_history
        )
        
        return {
            "query": query,
            "sql_query": sql_query,
            "results": results,
            "answer": answer,
            "used_history": use_history
        }

    def clear_chat_history(self):
        """Clear the chat history"""
        self.gemini_service.chat = self.gemini_service.model.start_chat(history=[])