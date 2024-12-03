import google.generativeai as genai
from ..config import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Initialized Gemini service")
        
        # Configure generation parameters
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Initialize model and chat
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=self.generation_config
        )
        self.chat = self.model.start_chat(history=[])

    async def process_query(self, query: str, schema: str, use_history: bool = False) -> str:
        """Process a query and return SQL"""
        logger.info(f"Processing query: {query}")
        logger.info(f"Using schema:\n{schema}")
        
        # Extract table name from schema
        table_name = schema.split('\n')[0].split(': ')[1].strip()
        
        prompt = f"""
        You are a SQL expert. Given this exact database schema:
        {schema}
        
        Write a SQL query for this request: "{query}"
        
        IMPORTANT RULES:
        1. The table name is exactly '{table_name}'
        2. Use only columns that exist in the schema above
        3. Return a simple SQL query without any formatting
        4. For text matching, use LOWER() function
        5. Don't use table aliases unless necessary
        6. Don't assume column names - use only those shown in the schema
        
        Example format:
        SELECT column1, column2 
        FROM {table_name} 
        WHERE LOWER(column_name) = LOWER('search_term')
        
        DO NOT use any columns or tables that are not shown in the schema above.
        """
        
        try:
            if use_history:
                sql_response = self.chat.send_message(prompt)
            else:
                sql_response = self.model.generate_content(prompt)
            
            sql_query = sql_response.text.strip()
            sql_query = sql_query.replace('```sql', '').replace('```', '')
            sql_query = sql_query.strip().rstrip(';')
            
            # Log the generated query
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Basic validation
            if not sql_query.lower().startswith('select'):
                logger.error("Generated query doesn't start with SELECT")
                return None
            if table_name not in sql_query:
                logger.error(f"Generated query doesn't use correct table name: {table_name}")
                return None
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return None

    async def generate_explanation(self,
                                 query: str,
                                 sql_query: Optional[str] = None,
                                 results: Optional[List[Dict]] = None,
                                 use_history: bool = False) -> str:
        """Generate an explanation of the results"""
        
        if sql_query and results:
            context = f"\nSQL Query: {sql_query}\nQuery Results: {results}"
            prompt = f"""
            Question: {query}
            {context}
            
            Analyze the data and provide a clear, natural response that:
            - Focuses on key business insights and trends
            - Explains numbers and calculations in plain language
            - Uses a friendly, conversational tone
            - Stays concise and to the point
            """
        else:
            prompt = f"""
            The user asked: {query}

            Please provide a friendly, brief response explaining that more information is needed 
            or ask them to rephrase their question if it's off-topic.
            """

        if use_history:
            response = self.chat.send_message(prompt)
        else:
            response = self.model.generate_content(prompt)
            
        return response.text.strip()