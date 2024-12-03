from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import query_routes, file_routes
from config import Settings

app = FastAPI()
settings = Settings()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query_routes.router)
app.include_router(file_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 