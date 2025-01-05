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
        
        # 打印当前工作目录和文件位置
        print("Current working directory:", Path.cwd())
        print("__file__ location:", Path(__file__))
        
        for file_path in possible_paths:
            print(f"Trying to load questions from: {file_path} (absolute: {file_path.absolute()})")
            try:
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    used_path = file_path
                    print(f"Successfully loaded from: {file_path}")
                    break
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if content is None:
            print("Failed to find quiz.md in any location, using fallback content")
            # 使用内置的示例题目作为备选
            content = """**第1章 绪论**

1. 题目：园林植物景观设计的主要任务是什么？
    * A、提供游憩场所
    * B、美化环境
    * C、创造优美的植物景观
    * D、以上都是
    答案：D

2. 题目：园林植物景观设计要遵循的基本原则不包括：
    * A、适地适树
    * B、因地制宜
    * C、统一协调
    * D、追求奢华
    答案：D

**第2章 基础知识**

1. 题目：下列哪种不是常见的园林植物配置形式？
    * A、花境
    * B、花坛
    * C、草坪
    * D、沙漠
    答案：D

2. 题目：植物群落的垂直结构从上到下正确的顺序是：
    * A、乔木层-灌木层-草本层-地被层
    * B、草本层-灌木层-乔木层-地被层
    * C、地被层-草本层-灌木层-乔木层
    * D、乔木层-草本层-灌木层-地被层
    答案：A"""
            
        print(f"Content length: {len(content)}")
        print("Content preview:", content[:200])
        
        # 更灵活的章节分割正则表达式
        chapter_pattern = r'\*\*第[一二三四五六七八九十\d]+章[^*]*\*\*'
        
        # 先找到所有章节标题
        chapter_titles = re.findall(chapter_pattern, content)
        print(f"Found chapter titles: {chapter_titles}")
        
        # 使用章节标题分割内容
        chapters = []
        last_end = 0
        for title in chapter_titles:
            start = content.find(title, last_end)
            if start == -1:
                continue
            if last_end > 0:
                chapters.append(content[last_end:start])
            last_end = start + len(title)
        # 添加最后一个章节
        if last_end < len(content):
            chapters.append(content[last_end:])
            
        print(f"Found {len(chapters)} chapters")
        
        if not chapters:
            print("Warning: No chapters found in content")
            print("Full content:", content)
            return []
            
        # 用于存储所有题目
        all_questions = []
        
        for chapter_idx, chapter_content in enumerate(chapters, 1):
            print(f"\nProcessing Chapter {chapter_idx}")
            print(f"Chapter content preview: {chapter_content[:200]}")
            
            # 使用更精确的题目匹配模式
            pattern = (
                r'(?:^|\n)\s*(\d+)\.\s*题目：(.*?)'  # 题号和题目
                r'(?:\n\s*\*\s*[A][\s.．、]\s*(.*?))'   # 选项A
                r'(?:\n\s*\*\s*[B][\s.．、]\s*(.*?))'   # 选项B
                r'(?:\n\s*\*\s*[C][\s.．、]\s*(.*?))'   # 选项C
                r'(?:\n\s*\*\s*[D][\s.．、]\s*(.*?))'   # 选项D
                r'(?:\n\s*答案：\s*([A-D]))'            # 答案
            )
            
            questions = list(re.finditer(pattern, chapter_content, re.DOTALL))
            print(f"Found {len(questions)} questions in chapter {chapter_idx}")
            
            for match in questions:
                num, question, a, b, c, d, answer = match.groups()
                print(f"Processing question {num}")
                
                # 清理题目文本
                clean_question = ' '.join(question.strip().split())
                
                # 清理选项文本
                clean_options = {
                    'A': ' '.join(a.strip().split()),
                    'B': ' '.join(b.strip().split()),
                    'C': ' '.join(c.strip().split()),
                    'D': ' '.join(d.strip().split())
                }
                
                formatted_q = {
                    'chapter': chapter_idx,
                    'number': num,
                    'question': clean_question,
                    'options': clean_options,
                    'correct_answer': answer
                }
                
                all_questions.append(formatted_q)
            
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