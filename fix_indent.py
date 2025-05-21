import re

def fix_indentation(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复generate_ai_analysis函数中的缩进问题
    pattern1 = r"        else:\s*\n\s*# 如果没有找到综合建议，使用全部内容\s*\n\s*analysis_result\[\"overall\"\] = content\s*\n\s*\n\s*return analysis_result\s*\n\s*else:"
    replacement1 = """            else:
                # 如果没有找到综合建议，使用全部内容
                analysis_result["overall"] = content
            
            return analysis_result
        else:"""
    
    content = re.sub(pattern1, replacement1, content)
    
    # 修复get_bazi_result函数中的缩进问题
    pattern2 = r"        # 构建提示词\s*\n\s*prompt = f\"\"\"\s*\n\s*请你作为一位专业的命理师"
    replacement2 = """        # 构建提示词
        prompt = f\"\"\"
        请你作为一位专业的命理师"""
    
    content = re.sub(pattern2, replacement2, content)
    
    pattern3 = r"        deepseek_api_key = os\.getenv\('DEEPSEEK_API_KEY', 'sk-[^']+'\)\s*\n\s*\n\s*payload = \{\s*\n\s*\"model\": \"deepseek-chat\",\s*\n\s*\"messages\": \[\s*\n\s*\{\"role\": \"system\""
    replacement3 = """        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-a70d312fd07b4bce82624bd2373a4db4')
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system\""""
    
    content = re.sub(pattern3, replacement3, content)
    
    pattern4 = r"        # 直接同步调用API\s*\n\s*response = requests\.post\(\s*\n\s*DEEPSEEK_API_URL,\s*\n\s*headers=headers,\s*\n\s*data=json\.dumps\(payload\),\s*\n\s*timeout=60  # 增加超时时间到60秒\s*\n\s*\)"
    replacement4 = """        # 直接同步调用API
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=60  # 增加超时时间到60秒
        )"""
    
    content = re.sub(pattern4, replacement4, content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复文件: {output_path}")

if __name__ == "__main__":
    fix_indentation("routes/bazi_routes.py", "routes/bazi_routes_fixed.py") 