import pandas as pd
from ..config import settings
import sqlite3
import tempfile
import os
from fastapi import UploadFile
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            logger.info("Initializing DataService")
            self.df = None
            self.conn = None
            self.temp_db = None
            self.table_name = None
            self.initialized = True
    
    def load_data(self, file_path: str):
        """Load data from file"""
        try:
            logger.info(f"Loading data from: {file_path}")
            
            # Set table name from file name (without extension)
            self.table_name = os.path.splitext(os.path.basename(file_path))[0]
            logger.info(f"Using table name: {self.table_name}")
            
            # Load the data
            self.df = pd.read_csv(file_path, encoding='latin1')
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            
            # Clean column names
            self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            self._preprocess_data()
            self._setup_sqlite()
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    async def update_data_source(self, file: UploadFile) -> str:
        """Handle new file upload and update the data source"""
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save uploaded file
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Load the new data
            self.load_data(file_path)
            
            return "File uploaded and processed successfully"
        except Exception as e:
            logger.error(f"Error updating data source: {str(e)}")
            raise

    def get_schema(self) -> str:
        """Get the current data schema"""
        if self.df is None:
            logger.warning("No data loaded. Please upload a file first.")
            return "No data loaded. Please upload a file first."
        
        # Get column info
        columns = self.df.columns.tolist()
        dtypes = self.df.dtypes.tolist()
        
        # Log column information
        logger.info(f"Table name: {self.table_name}")
        logger.info("Available columns:")
        for col, dtype in zip(columns, dtypes):
            logger.info(f"- {col} ({dtype})")
        
        # Create schema string
        schema = f"Table name: {self.table_name}\nColumns:\n"
        for col, dtype in zip(columns, dtypes):
            schema += f"- {col} ({dtype})\n"
        
        return schema

    def execute_query(self, sql_query: str) -> list:
        """Execute SQL query on the data"""
        if self.df is None or self.conn is None:
            raise Exception("No data loaded. Please upload a file first.")
        
        try:
            logger.info(f"Executing SQL query: {sql_query}")
            
            # Log table info
            logger.info("\nTable info:")
            sample_query = f"SELECT * FROM {self.table_name} LIMIT 1"
            logger.info(f"Sample query: {sample_query}")
            sample_data = pd.read_sql_query(sample_query, self.conn)
            logger.info(f"Sample data:\n{sample_data}")
            
            # Execute the actual query
            result = pd.read_sql_query(sql_query, self.conn)
            logger.info(f"Query results shape: {result.shape}")
            
            if result.empty:
                logger.warning("Query returned no results")
                return []
            
            return result.to_dict('records')
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            raise

    def _preprocess_data(self):
        """Preprocess the data"""
        try:
            logger.info("Starting data preprocessing...")
            
            # First identify date columns by name pattern
            potential_date_cols = [col for col in self.df.columns if any(date_term in col.lower() for date_term in ['date', 'time', 'year'])]
            
            # Convert date columns
            for col in potential_date_cols:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    logger.info(f"Converted {col} to datetime")
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to datetime: {str(e)}")

            # Identify and convert numeric columns
            for col in self.df.columns:
                # Skip already converted date columns
                if col in potential_date_cols:
                    continue
                    
                # Try to convert to numeric if more than 80% of non-null values are numeric
                try:
                    numeric_count = pd.to_numeric(self.df[col], errors='coerce').notna().sum()
                    total_count = self.df[col].notna().sum()
                    if total_count > 0 and numeric_count / total_count > 0.8:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                        logger.info(f"Converted {col} to numeric")
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to numeric: {str(e)}")

            # Handle missing values appropriately based on column type
            for col in self.df.columns:
                if self.df[col].dtype == 'datetime64[ns]':
                    # For date columns, fill with a sensible default or leave as NaT
                    self.df[col] = self.df[col].fillna(pd.NaT)
                elif pd.api.types.is_numeric_dtype(self.df[col]):
                    # For numeric columns, fill with 0 or mean depending on context
                    self.df[col] = self.df[col].fillna(0)
                else:
                    # For string/categorical columns, fill with empty string
                    self.df[col] = self.df[col].fillna('')

            logger.info("Data preprocessing completed successfully")
            logger.info(f"Final datatypes:\n{self.df.dtypes}")

        except Exception as e:
            logger.error(f"Error in preprocessing data: {str(e)}")
            raise

    def _setup_sqlite(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.conn = sqlite3.connect(self.temp_db.name)
        self.df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)
        
        # Create helpful views for common queries
        self._create_views()

    def _create_views(self):
        """Create views based on actual columns"""
        try:
            # Get actual column names from the dataframe
            columns = self.df.columns.tolist()
            
            # Create dynamic views based on available columns
            views = []
            
            # Only create views if required columns exist
            if 'order_date' in columns:
                views.append(f"""
                    CREATE VIEW IF NOT EXISTS yearly_orders AS
                    SELECT strftime('%Y', order_date) as year, COUNT(*) as total_orders
                    FROM {self.table_name}
                    GROUP BY year
                """)
            
            if 'customer_name' in columns and 'sales' in columns:
                views.append(f"""
                    CREATE VIEW IF NOT EXISTS customer_orders AS
                    SELECT customer_name, COUNT(*) as order_count, SUM(sales) as total_sales
                    FROM {self.table_name}
                    GROUP BY customer_name
                """)
            
            # Execute views that can be created
            for view in views:
                try:
                    self.conn.execute(view)
                except Exception as e:
                    logger.error(f"Failed to create view: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error creating views: {str(e)}")

    def __del__(self):
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            if hasattr(self, 'temp_db') and self.temp_db:
                os.unlink(self.temp_db.name)
        except Exception:
            pass 