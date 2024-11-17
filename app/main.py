from fastapi import FastAPI
from models import BaseSQL, engine

app = FastAPI(
    title="My_app",
    description="My description",
    version="0.0.1",
)

@app.get("/")
async def root():
    return {"message": "Hello World"}