import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from datetime import datetime
from quiz import load_questions, load_wrong_questions, save_wrong_questions

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("园林植物景观设计测验")
        self.root.geometry("800x600")
        
        # 加载题目
        self.questions = load_questions('quiz.md')
        self.current_question = None
        self.score = 0
        self.question_index = 0
        self.selected_questions = []
        self.shuffled_options = None
        self.shuffled_answer = None
        self.wrong_questions = {}
        
        self.create_main_menu()
        
    def create_main_menu(self):
        self.clear_window()
        
        # 创建主菜单框架
        menu_frame = ttk.Frame(self.root, padding="20")
        menu_frame.pack(expand=True)
        
        ttk.Label(menu_frame, text="园林植物景观设计测验", font=('Arial', 20)).pack(pady=20)
        
        # 主菜单按钮
        ttk.Button(menu_frame, text="开始新测验", command=self.show_chapter_selection).pack(pady=10, ipadx=20)
        ttk.Button(menu_frame, text="练习错题", command=self.start_wrong_questions).pack(pady=10, ipadx=20)
        ttk.Button(menu_frame, text="退出", command=self.root.quit).pack(pady=10, ipadx=20)
        
    def show_chapter_selection(self):
        self.clear_window()
        
        chapter_frame = ttk.Frame(self.root, padding="20")
        chapter_frame.pack(expand=True)
        
        ttk.Label(chapter_frame, text="选择章节", font=('Arial', 16)).pack(pady=20)
        
        chapters = sorted(set(q['chapter'] for q in self.questions))
        
        def select_chapter(chapter=None):
            if chapter is None:  # 全部章节
                self.selected_questions = self.questions.copy()  # 创建副本以免影响原始题目顺序
            else:
                self.selected_questions = [q for q in self.questions if q['chapter'] == chapter]
            self.start_quiz()
        
        ttk.Button(chapter_frame, text="全部章节", 
                  command=lambda: select_chapter()).pack(pady=5)
        
        for chapter in chapters:
            chapter_questions = [q for q in self.questions if q['chapter'] == chapter]
            ttk.Button(chapter_frame, 
                      text=f"第{chapter}章 ({len(chapter_questions)}题)",
                      command=lambda c=chapter: select_chapter(c)).pack(pady=5)
        
        ttk.Button(chapter_frame, text="返回", command=self.create_main_menu).pack(pady=20)
        
    def start_quiz(self):
        self.question_index = 0
        self.score = 0
        self.wrong_questions = {}
        
        # 使用当前时间作为随机种子
        random.seed(datetime.now().timestamp())
        # 随机打乱题目顺序
        random.shuffle(self.selected_questions)
        
        self.show_question()
        
    def start_wrong_questions(self):
        wrong_questions = load_wrong_questions()
        if not wrong_questions:
            messagebox.showinfo("提示", "错题本中还没有题目！")
            return
            
        self.selected_questions = [q for q in self.questions if q['number'] in wrong_questions]
        random.shuffle(self.selected_questions)
        self.start_quiz()
        
    def show_question(self):
        self.clear_window()
        
        if self.question_index >= len(self.selected_questions):
            self.show_result()
            return
            
        question = self.selected_questions[self.question_index]
        self.current_question = question
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        # 创建上部分框架（用于显示题目和选项）
        question_frame = ttk.Frame(self.main_frame)
        question_frame.pack(expand=True, fill='both')
        
        # 创建下部分框架（用于显示答题结果）
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_frame.pack(fill='x', pady=10)
        
        # 显示进度
        progress_text = f"第{self.question_index + 1}/{len(self.selected_questions)}题"
        ttk.Label(question_frame, text=progress_text, font=('Arial', 14)).pack(pady=5)
        
        # 显示题目
        question_text = f"第{question['chapter']}章 第{question['number']}题:\n{question['question']}"
        ttk.Label(question_frame, text=question_text, wraplength=700, font=('Arial', 14)).pack(pady=20)
        
        # 创建选项框架
        options_frame = ttk.Frame(question_frame)
        options_frame.pack(fill='both', expand=True, padx=40)
        
        # 随机打乱选项
        options = question['options']
        options_list = [(key, value) for key, value in options.items()]
        correct_content = options[question['correct_answer']]
        random.shuffle(options_list)
        
        self.shuffled_options = {chr(65+i): content for i, (_, content) in enumerate(options_list)}
        self.shuffled_answer = next(key for key, value in self.shuffled_options.items() 
                                  if value == correct_content)
        
        # 选项按钮
        self.answer_var = tk.StringVar()
        self.answer_var.trace('w', lambda *args: self.check_answer())
        
        style = ttk.Style()
        style.configure('Custom.TRadiobutton', font=('Arial', 12), padding=10)
        
        for key, value in self.shuffled_options.items():
            option_frame = ttk.Frame(options_frame)
            option_frame.pack(fill='x', pady=10)
            
            radio = ttk.Radiobutton(option_frame, 
                                   text=f"{key}. {value}", 
                                   variable=self.answer_var, 
                                   value=key,
                                   style='Custom.TRadiobutton')
            radio.pack(side='left', padx=20, fill='x', expand=True)
        
    def check_answer(self):
        answer = self.answer_var.get()
        if not answer:
            return
            
        question = self.current_question
        
        # 清除之前的结果显示
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        if answer == self.shuffled_answer:
            self.score += 1
            result_text = "✓ 回答正确！点击任意位置继续"
            label = ttk.Label(self.result_frame, text=result_text, 
                             font=('Arial', 14, 'bold'), foreground='green')
        else:
            result_text = f"✗ 回答错误。正确答案是：{self.shuffled_answer}\n点击任意位置继续"
            label = ttk.Label(self.result_frame, text=result_text, 
                             font=('Arial', 14, 'bold'), foreground='red')
            self.wrong_questions[question['number']] = {
                'chapter': question['chapter'],
                'question': question['question'],
                'options': self.shuffled_options,
                'correct_answer': self.shuffled_answer,
                'your_answer': answer
            }
        
        label.pack(pady=10)
        
        # 禁用所有选项
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Radiobutton):
                widget.configure(state='disabled')
        
        # 绑定点击事件到整个窗口
        self.root.bind('<Button-1>', self.handle_click)
        
    def handle_click(self, event):
        # 解绑点击事件
        self.root.unbind('<Button-1>')
        # 显示下一题
        self.next_question()
        
    def next_question(self):
        self.question_index += 1
        self.show_question()
        
    def show_result(self):
        self.clear_window()
        
        result_frame = ttk.Frame(self.root, padding="20")
        result_frame.pack(expand=True, fill='both')
        
        # 显示得分
        score_text = f"测验完成！\n最终得分：{self.score}/{len(self.selected_questions)}"
        ttk.Label(result_frame, text=score_text, font=('Arial', 16)).pack(pady=20)
        
        # 显示错题
        if self.wrong_questions:
            wrong_text = f"\n本次做错{len(self.wrong_questions)}道题："
            ttk.Label(result_frame, text=wrong_text).pack(pady=10)
            
            # 创建错题显示区域（可滚动）
            canvas = tk.Canvas(result_frame)
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 添加鼠标滚轮绑定
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # 当鼠标离开canvas时解绑滚轮事件
            def _unbound_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            
            # 当鼠标进入canvas时绑定滚轮事件
            def _bound_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            canvas.bind('<Enter>', _bound_mousewheel)
            canvas.bind('<Leave>', _unbound_mousewheel)
            
            for num, wrong_q in self.wrong_questions.items():
                question_text = f"\n第{wrong_q['chapter']}章 第{num}题:\n{wrong_q['question']}"
                ttk.Label(scrollable_frame, text=question_text, wraplength=600).pack(pady=5)
                
                for key, value in wrong_q['options'].items():
                    option_text = f"{key}. {value}"
                    ttk.Label(scrollable_frame, text=option_text, wraplength=600).pack(pady=2)
                
                answer_text = f"正确答案：{wrong_q['correct_answer']}\n你的答案：{wrong_q['your_answer']}"
                ttk.Label(scrollable_frame, text=answer_text).pack(pady=5)
            
            canvas.pack(side="left", fill="both", expand=True, pady=10)
            scrollbar.pack(side="right", fill="y")
            
            # 保存错题
            save_wrong_questions(self.wrong_questions)
        
        # 返回主菜单按钮
        ttk.Button(result_frame, text="返回主菜单", command=self.create_main_menu).pack(pady=20)
        
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop() 