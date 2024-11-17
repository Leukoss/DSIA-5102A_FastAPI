from fastapi import FastAPI
from models import BaseSQL, engine

app = FastAPI(
    title="My_app",
    description="My description",
    version="0.0.1",
)

@app.on_event("startup")
async def startup_event():
    BaseSQL.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}