from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api.router import api
from .core.database import close_connection_pool
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    yield
    # Shutdown
    print("🛑 Shutting down...")
    close_connection_pool()

app = FastAPI(
    title="Bug-Free Blog API", 
    description="A robust blog backend API with authentication and user management", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:3001",  # Alternative React port
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Vue.js default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add your production frontend URL when ready
        # "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api)

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()
