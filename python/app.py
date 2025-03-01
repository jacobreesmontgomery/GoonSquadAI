"""
CLASS: app.py
AUTHOR: Jacob Montgomery
OVERVIEW: This file will drive the front-end webpage.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from routes.activities import activities_router
from routes.chat import chat_router

app = FastAPI(
    title="API Documentation",
    description="This API enables users to get valuable information about their activities.",
    version="1.0.0",
    docs_url="/docs",  # Custom URL for Swagger UI
    redoc_url="/redoc",  # Custom URL for ReDoc
    openapi_url="/openapi.json",  # Custom OpenAPI schema URL
)

app.include_router(
    router=activities_router,
    prefix="/api/v1",
    tags=["Activities"],
)
app.include_router(
    router=chat_router,
    prefix="/api/v1",
    tags=["Chat"],
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to restrict allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    run(app, host="localhost", port=5000)
