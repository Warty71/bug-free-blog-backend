from fastapi import FastAPI
from app.api.router import api

app = FastAPI(title="API", description="First API I've made.", version="0.1.0")
app.include_router(api)

def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
