from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from executor import run_pipeline
from database import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(
    title="Text-to-SQL API",
    description="Natural language to SQL pipeline using Gemini + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
async def root():
    return {"message": "Text-to-SQL API is running. POST to /query with {question: '...'}"}


@app.post("/query")
async def query(request: QueryRequest):
    result = await run_pipeline(request.question)
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}