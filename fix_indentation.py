#!/usr/bin/env python
# 修复缩进问题的Python脚本

with open('routes/bazi_routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找问题行
problem_line = -1
for i, line in enumerate(lines):
    if "# 如果没有PDF URL，先生成PDF" in line:
        problem_line = i
        break

if problem_line > 0:
    # 确保try块中的代码有正确缩进
    for i in range(problem_line + 2, len(lines)):
        if "from utils.pdf_generator import generate_pdf" in line:
            # 修复缩进
            lines[i] = "        " + lines[i].lstrip()
            print(f"修复了第 {i+1} 行的缩进")
            break

    # 保存修改后的文件
    with open('routes/bazi_routes.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("文件已修复")
else:
    print("未找到问题行") 