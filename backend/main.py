from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random
from datetime import datetime
from pathlib import Path

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_questions():
    with open(Path(__file__).parent / "data/quiz.md", "r", encoding="utf-8") as f:
        content = f.read()
    # 这里保留原来的题目解析逻辑
    # ...
    return questions

@app.get("/api/questions")
async def get_questions():
    questions = load_questions()
    return {"questions": questions}

@app.get("/api/questions/{chapter}")
async def get_chapter_questions(chapter: int):
    questions = load_questions()
    chapter_questions = [q for q in questions if q["chapter"] == chapter]
    return {"questions": chapter_questions}

@app.post("/api/wrong-questions")
async def save_wrong_questions(wrong_questions: dict):
    # 保存错题逻辑
    return {"status": "success"} 