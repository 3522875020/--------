import re
import json
import os
from datetime import datetime
import random

def load_questions(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按章节分割内容
    chapters = re.split(r'\*\*第.*?章.*?\*\*', content)[1:]
    
    # 用于存储所有题目
    all_questions = []
    question_map = {}
    
    for chapter_idx, chapter_content in enumerate(chapters, 1):
        # 提取题目
        pattern = r'(\d+)\.\s+题目：(.*?)\n\s+\*\s+A、(.*?)\n\s+\*\s+B、(.*?)\n\s+\*\s+C、(.*?)\n\s+\*\s+D、(.*?)\n\s+答案：([A-D])'
        questions = re.findall(pattern, chapter_content, re.DOTALL)
        
        for q in questions:
            num, question, a, b, c, d, answer = q
            
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
    
    # 按题号排序
    all_questions.sort(key=lambda x: (x['chapter'], int(x['number'])))
    
    if not all_questions:
        print("警告：没有找到任何题目！")
        print("正在打印文件内容的一部分用于调试：")
        print(content[:500])
    else:
        print(f"\n成功加载 {len(all_questions)} 道题目")
        print(f"共 {len(set(q['chapter'] for q in all_questions))} 章")
        
        # 显示每章题目数量
        chapter_counts = {}
        for q in all_questions:
            chapter_counts[q['chapter']] = chapter_counts.get(q['chapter'], 0) + 1
        
        for chapter, count in sorted(chapter_counts.items()):
            print(f"第{chapter}章：{count}题")
    
    return all_questions

def save_progress(progress):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quiz_progress_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    return filename

def load_progress(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_saved_progress():
    progress_files = [f for f in os.listdir() if f.startswith('quiz_progress_') and f.endswith('.json')]
    return sorted(progress_files, reverse=True)  # 最新的在前面

def save_wrong_questions(wrong_questions):
    filename = "wrong_questions.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            existing_wrong = json.load(f)
        # 合并现有错题和新错题，保留正确次数
        for num, q in wrong_questions.items():
            if num in existing_wrong:
                q['correct_count'] = existing_wrong[num].get('correct_count', 0)
            else:
                q['correct_count'] = 0
    else:
        # 新增错题默认正确次数为0
        for q in wrong_questions.values():
            q['correct_count'] = 0
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(wrong_questions, f, ensure_ascii=False, indent=2)

def load_wrong_questions():
    filename = "wrong_questions.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def shuffle_options(options, correct_answer):
    """随机打乱选项并返回新的选项和正确答案"""
    # 创建选项列表
    options_list = [(key, value) for key, value in options.items()]
    # 记住正确答案对应的选项内容
    correct_content = options[correct_answer]
    # 打乱选项
    random.shuffle(options_list)
    
    # 创建新的选项字典
    new_options = {chr(65+i): content for i, (_, content) in enumerate(options_list)}
    # 找到正确答案的新选项字母
    new_correct = next(key for key, value in new_options.items() if value == correct_content)
    
    return new_options, new_correct

def practice_questions(questions, wrong_questions=None, start_from=0):
    score = 0
    total = len(questions)
    answers = {}
    new_wrong_questions = {}
    
    # 加载自动保存的进度
    auto_save_file = "auto_save.json"
    if os.path.exists(auto_save_file) and start_from == 0:
        try:
            with open(auto_save_file, 'r', encoding='utf-8') as f:
                auto_save = json.load(f)
                if input("\n发现上次的自动保存进度，是否继续？(y/n): ").lower() == 'y':
                    score = auto_save['score']
                    start_from = auto_save['current_question']
                    answers = auto_save['answers']
        except:
            pass
    
    print(f"\n共{total}道题目，从第{start_from+1}题开始")
    
    try:
        for i in range(start_from, total):
            q = questions[i]
            # 随机打乱选项
            shuffled_options, shuffled_answer = shuffle_options(q['options'], q['correct_answer'])
            
            print(f"\n第{q['chapter']}章 第{q['number']}题: {q['question']}")
            print(f"A. {shuffled_options['A']}")
            print(f"B. {shuffled_options['B']}")
            print(f"C. {shuffled_options['C']}")
            print(f"D. {shuffled_options['D']}")
            
            while True:
                answer = input("\n请输入你的答案(A/B/C/D)，或输入S保存进度，Q退出: ").strip().upper()
                if answer in ['A', 'B', 'C', 'D', 'S', 'Q']:
                    break
                print("输入无效，请输入A、B、C、D或S保存进度，Q退出")
            
            if answer == 'S':
                progress = {
                    'score': score,
                    'current_question': i,
                    'answers': answers,
                    'total': total
                }
                saved_file = save_progress(progress)
                print(f"\n进度已保存到文件：{saved_file}")
                break
                
            if answer == 'Q':
                print("\n已退出测验")
                break
            
            answers[q['number']] = answer
            
            if answer == shuffled_answer:  # 使用打乱后的正确答案
                print("✓ 回答正确！")
                score += 1
                if wrong_questions and q['number'] in wrong_questions:
                    del wrong_questions[q['number']]
            else:
                print(f"✗ 回答错误。正确答案是：{shuffled_answer}")  # 显示打乱后的正确答案
                new_wrong_questions[q['number']] = {
                    'chapter': q['chapter'],
                    'question': q['question'],
                    'options': shuffled_options,  # 保存打乱后的选项顺序
                    'correct_answer': shuffled_answer,  # 保存打乱后的正确答案
                    'your_answer': answer
                }
            
            print(f"当前得分：{score}/{total}")
            
            # 自动保存进度
            auto_save = {
                'score': score,
                'current_question': i + 1,  # 保存下一题的位置
                'answers': answers,
                'total': total,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(auto_save, f, ensure_ascii=False, indent=2)
    
    except KeyboardInterrupt:
        print("\n\n测验被中断")
        # 中断时也保存进度
        auto_save = {
            'score': score,
            'current_question': i,
            'answers': answers,
            'total': total,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(auto_save_file, 'w', encoding='utf-8') as f:
            json.dump(auto_save, f, ensure_ascii=False, indent=2)
        
    if i == total - 1:
        print(f"\n测验完成！最终得分：{score}/{total}")
        # 输出错题汇总
        if new_wrong_questions:
            print("\n错题汇总：")
            for num, wrong_q in new_wrong_questions.items():
                print(f"\n第{wrong_q['chapter']}章 第{num}题: {wrong_q['question']}")
                print(f"A. {wrong_q['options']['A']}")
                print(f"B. {wrong_q['options']['B']}")
                print(f"C. {wrong_q['options']['C']}")
                print(f"D. {wrong_q['options']['D']}")
                print(f"正确答案：{wrong_q['correct_answer']}")
                print(f"你的答案：{wrong_q['your_answer']}")
            print(f"\n共{len(new_wrong_questions)}道错题，已加入错题本")
        # 删除自动保存文件
        if os.path.exists(auto_save_file):
            os.remove(auto_save_file)
    
    return score, total

def practice_wrong_questions(questions, wrong_questions):
    score = 0
    # 使用伪随机抽取错题
    wrong_questions_list = list(wrong_questions.items())
    random.seed(datetime.now().timestamp())  # 使用当前时间作为随机种子
    random.shuffle(wrong_questions_list)
    
    total = len(wrong_questions_list)
    print(f"\n共{total}道错题")
    
    try:
        wrong_in_practice = {}  # 记录本次练习做错的题目
        for num, wrong_q in wrong_questions_list:
            q = next((q for q in questions if q['number'] == num), None)
            if not q:
                continue
            
            # 随机打乱选项
            shuffled_options, shuffled_answer = shuffle_options(q['options'], q['correct_answer'])
            
            print(f"\n第{q['chapter']}章 第{q['number']}题: {q['question']}")
            print(f"A. {shuffled_options['A']}")
            print(f"B. {shuffled_options['B']}")
            print(f"C. {shuffled_options['C']}")
            print(f"D. {shuffled_options['D']}")
            
            while True:
                answer = input("\n请输入你的答案(A/B/C/D)，或输入Q退出: ").strip().upper()
                if answer in ['A', 'B', 'C', 'D', 'Q']:
                    break
                print("输入无效，请输入A、B、C、D或Q退出")
            
            if answer == 'Q':
                print("\n已退出练习")
                break
            
            if answer == shuffled_answer:  # 使用打乱后的正确答案
                print("✓ 回答正确！")
                score += 1
                wrong_q['correct_count'] = wrong_q.get('correct_count', 0) + 1
                if wrong_q['correct_count'] >= 3:
                    print(f"恭喜！此题已连续答对3次，将从错题本中移除")
                    del wrong_questions[num]
                else:
                    wrong_q['your_answer'] = answer
                    wrong_questions[num] = wrong_q
            else:
                print(f"✗ 回答错误。正确答案是：{shuffled_answer}")  # 显示打乱后的正确答案
                wrong_q['correct_count'] = 0
                wrong_q['your_answer'] = answer
                wrong_questions[num] = wrong_q
            
            print(f"当前得分：{score}/{total}")
            
            # 保存最新状态
            save_wrong_questions(wrong_questions)
            
            if answer != shuffled_answer:
                wrong_in_practice[num] = {
                    'chapter': q['chapter'],
                    'question': q['question'],
                    'options': q['options'],
                    'correct_answer': q['correct_answer'],
                    'your_answer': answer
                }
    
    except KeyboardInterrupt:
        print("\n\n练习被中断")
        save_wrong_questions(wrong_questions)
    
    print(f"\n练习完成！最终得分：{score}/{total}")
    
    # 输出本次练习的错题汇总
    if wrong_in_practice:
        print("\n本次练习错题汇总：")
        for num, wrong_q in wrong_in_practice.items():
            print(f"\n第{wrong_q['chapter']}章 第{num}题: {wrong_q['question']}")
            print(f"A. {wrong_q['options']['A']}")
            print(f"B. {wrong_q['options']['B']}")
            print(f"C. {wrong_q['options']['C']}")
            print(f"D. {wrong_q['options']['D']}")
            print(f"正确答案：{wrong_q['correct_answer']}")
            print(f"你的答案：{wrong_q['your_answer']}")
        print(f"\n本次练习共做错{len(wrong_in_practice)}道题")
    
    return score, total

def quiz():
    while True:
        print("\n1. 开始新测验")
        print("2. 继续上次测验")
        print("3. 练习错题")
        print("4. 退出")
        
        choice = input("\n请选择(1-4): ").strip()
        
        if choice == '4':
            print("再见！")
            break
            
        questions = load_questions('quiz.md')
        if not questions:
            print("没有找到题目，请检查题库格式或文件路径")
            return
        
        if choice == '1':
            # 显示章节选择菜单
            chapters = sorted(set(q['chapter'] for q in questions))
            print("\n请选择要测试的章节：")
            print("0. 全部章节")
            for chapter in chapters:
                chapter_questions = [q for q in questions if q['chapter'] == chapter]
                print(f"{chapter}. 第{chapter}章 ({len(chapter_questions)}题)")
            
            while True:
                try:
                    chapter_choice = int(input("\n请输入章节编号: "))
                    if chapter_choice == 0:
                        selected_questions = questions
                        break
                    elif chapter_choice in chapters:
                        selected_questions = [q for q in questions if q['chapter'] == chapter_choice]
                        break
                    print(f"请输入0-{max(chapters)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            practice_questions(selected_questions)
            
        elif choice == '2':
            saved_files = list_saved_progress()
            if not saved_files:
                print("没有找到保存的进度！")
                continue
                
            print("\n找到以下保存的进度：")
            for i, f in enumerate(saved_files, 1):
                print(f"{i}. {f}")
                
            while True:
                try:
                    file_choice = int(input("\n请选择要继续的进度(输入数字): "))
                    if 1 <= file_choice <= len(saved_files):
                        progress = load_progress(saved_files[file_choice-1])
                        questions = questions[progress['current_question']:]
                        practice_questions(questions)
                        break
                    print(f"请输入1-{len(saved_files)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
                    
        elif choice == '3':
            wrong_questions = load_wrong_questions()
            if not wrong_questions:
                print("错题本中还没有题目！")
                continue
            
            # 显示错题的章节分布
            wrong_chapters = {}
            for num, q in wrong_questions.items():
                chapter = q['chapter']
                wrong_chapters[chapter] = wrong_chapters.get(chapter, 0) + 1
            
            print("\n错题分布：")
            print("0. 全部错题")
            for chapter, count in sorted(wrong_chapters.items()):
                print(f"{chapter}. 第{chapter}章 ({count}题)")
            
            while True:
                try:
                    chapter_choice = int(input("\n请选择要练习的章节: "))
                    if chapter_choice == 0:
                        selected_wrong = wrong_questions
                        break
                    elif chapter_choice in wrong_chapters:
                        selected_wrong = {num: q for num, q in wrong_questions.items() 
                                       if q['chapter'] == chapter_choice}
                        break
                    print(f"请输入0-{max(wrong_chapters.keys())}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            practice_wrong_questions(questions, selected_wrong)

if __name__ == '__main__':
    print("欢迎参加园林植物景观设计测验！")
    quiz() 