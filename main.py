from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import query_routes, file_routes

app = FastAPI(title="RAG API", description="Natural Language to SQL Query API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query_routes.router, prefix="/api/v1", tags=["queries"])
app.include_router(file_routes.router, prefix="/api/v1/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"} 