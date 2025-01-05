from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random
from datetime import datetime
from pathlib import Path
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_questions():
    try:
        file_path = Path(__file__).parent / "data/quiz.md"
        print(f"Trying to load questions from: {file_path}")
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return []
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Content length: {len(content)}")
            
        # 按章节分割内容
        chapters = re.split(r'\*\*第.*?章.*?\*\*', content)[1:]
        print(f"Found {len(chapters)} chapters")
        
        # 用于存储所有题目
        all_questions = []
        
        for chapter_idx, chapter_content in enumerate(chapters, 1):
            # 提取题目
            pattern = r'(\d+)\.\s+题目：(.*?)\n\s+\*\s+A、(.*?)\n\s+\*\s+B、(.*?)\n\s+\*\s+C、(.*?)\n\s+\*\s+D、(.*?)\n\s+答案：([A-D])'
            questions = re.findall(pattern, chapter_content, re.DOTALL)
            print(f"Chapter {chapter_idx}: Found {len(questions)} questions")
            
            for q in questions:
                num, question, a, b, c, d, answer = q
                
                # 清理题目文本
                clean_question = ' '.join(question.strip().split())
                
                formatted_q = {
                    'chapter': chapter_idx,
                    'number': num,
                    'question': clean_question,
                    'options': {
                        'A': a.strip(),
                        'B': b.strip(),
                        'C': c.strip(),
                        'D': d.strip()
                    },
                    'correct_answer': answer
                }
                
                all_questions.append(formatted_q)
        
        print(f"Total questions loaded: {len(all_questions)}")
        return all_questions
    except Exception as e:
        print(f"Error loading questions: {e}")
        import traceback
        print(traceback.format_exc())
        return []

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.get("/api/test")
async def test():
    questions = load_questions()
    return {
        "status": "ok",
        "questions_count": len(questions),
        "first_question": questions[0] if questions else None
    }

@app.get("/api/questions")
async def get_questions():
    questions = load_questions()
    if not questions:
        return {"error": "Failed to load questions"}
    return {"questions": questions}

@app.get("/api/chapters")
async def get_chapters():
    questions = load_questions()
    if not questions:
        return {"error": "Failed to load questions"}
    chapters = sorted(set(q["chapter"] for q in questions))
    return {"chapters": chapters}

@app.get("/api/questions/{chapter}")
async def get_chapter_questions(chapter: int):
    questions = load_questions()
    if not questions:
        return {"error": "Failed to load questions"}
    chapter_questions = [q for q in questions if q["chapter"] == chapter]
    return {"questions": chapter_questions}

@app.post("/api/wrong-questions")
async def save_wrong_questions(wrong_questions: dict):
    return {"status": "success"} 