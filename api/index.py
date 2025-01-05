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
        # 尝试多个可能的文件位置
        possible_paths = [
            Path(__file__).parent / "data/quiz.md",
            Path(__file__).parent.parent / "quiz.md",
            Path(__file__).parent / "quiz.md",
        ]
        
        content = None
        used_path = None
        
        for file_path in possible_paths:
            print(f"Trying to load questions from: {file_path}")
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                used_path = file_path
                print(f"Successfully loaded from: {file_path}")
                break
        
        if content is None:
            print("Failed to find quiz.md in any location")
            print("Searched paths:", possible_paths)
            return []
            
        print(f"Content length: {len(content)}")
        
        # 按章节分割内容，使用更精确的正则表达式
        chapters = re.split(r'\*\*第\s*\d+\s*章[^*]*\*\*', content)[1:]
        print(f"Found {len(chapters)} chapters")
        
        if not chapters:
            print("Warning: No chapters found in content")
            print("Content preview:", content[:500])
            return []
            
        # 用于存储所有题目
        all_questions = []
        question_map = {}
        
        for chapter_idx, chapter_content in enumerate(chapters, 1):
            # 使用更精确的题目匹配模式
            pattern = (
                r'(?:^|\n)\s*(\d+)\.\s*题目：(.*?)'  # 题号和题目
                r'(?:\n\s*\*\s*A[、．.]\s*(.*?))?'   # 选项A
                r'(?:\n\s*\*\s*B[、．.]\s*(.*?))?'   # 选项B
                r'(?:\n\s*\*\s*C[、．.]\s*(.*?))?'   # 选项C
                r'(?:\n\s*\*\s*D[、．.]\s*(.*?))?'   # 选项D
                r'\n\s*答案：\s*([A-D])'             # 答案
            )
            
            questions = re.finditer(pattern, chapter_content, re.DOTALL)
            question_count = 0
            
            for match in questions:
                question_count += 1
                num, question, a, b, c, d, answer = match.groups()
                
                # 确保所有选项都存在
                if not all([a, b, c, d]):
                    print(f"警告：第{chapter_idx}章第{num}题选项不完整")
                    continue
                
                # 清理题目文本
                clean_question = ' '.join(question.strip().split())
                
                # 清理选项文本
                clean_options = {
                    'A': ' '.join(a.strip().split()),
                    'B': ' '.join(b.strip().split()),
                    'C': ' '.join(c.strip().split()),
                    'D': ' '.join(d.strip().split())
                }
                
                # 检查重复和矛盾
                if clean_question in question_map:
                    existing_q = question_map[clean_question]
                    if existing_q['correct_answer'] != answer:
                        print(f"\n警告：发现答案矛盾的题目：")
                        print(f"题号 {existing_q['number']} 和 {num}")
                        print(f"题目：{clean_question}")
                        print(f"答案分别为：{existing_q['correct_answer']} 和 {answer}")
                        continue
                    else:
                        print(f"\n警告：发现重复的题目：")
                        print(f"题号 {existing_q['number']} 和 {num}")
                        continue
                
                formatted_q = {
                    'chapter': chapter_idx,
                    'number': num,
                    'question': clean_question,
                    'options': clean_options,
                    'correct_answer': answer
                }
                
                question_map[clean_question] = formatted_q
                all_questions.append(formatted_q)
            
            print(f"Chapter {chapter_idx}: Found {question_count} questions")
        
        # 按题号排序
        all_questions.sort(key=lambda x: (x['chapter'], int(x['number'])))
        
        print(f"Total questions loaded: {len(all_questions)}")
        return all_questions
    except Exception as e:
        print(f"Error loading questions: {e}")
        import traceback
        print(traceback.format_exc())
        return []

@app.get("/")
async def root():
    return {
        "status": "API is running",
        "message": "Use /api/questions to get questions"
    }

@app.get("/api/test")
async def test():
    """测试端点，用于检查API状态和题目加载"""
    try:
        questions = load_questions()
        return {
            "status": "ok",
            "questions_count": len(questions),
            "first_question": questions[0] if questions else None,
            "chapters": sorted(set(q["chapter"] for q in questions)) if questions else []
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
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