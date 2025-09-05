from contextlib import asynccontextmanager
from fastapi import FastAPI
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
    title="API", 
    description="First API I've made.", 
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(api)

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()
