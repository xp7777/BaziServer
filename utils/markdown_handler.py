import logging
import re
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建markdown解析器实例
md = MarkdownIt('commonmark', {'html': True, 'breaks': True, 'typographer': True})
renderer = RendererHTML()

def parse_markdown(text):
    """
    将Markdown文本解析为HTML，特殊处理八字分析格式
    
    Args:
        text: Markdown格式的文本
        
    Returns:
        str: 转换后的HTML文本
    """
    if not text:
        return ""
    
    try:
        # 检查内容是否已经是HTML
        if text.strip().startswith('<') and text.strip().endswith('>') and ('<div' in text or '<p>' in text):
            # 如果是HTML，直接返回
            return text
            
        # 预处理八字分析特殊格式
        processed_text = text
        
        # 处理加粗文本 **文本**
        processed_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed_text)
        
        # 处理分隔符 -- 转换为水平线
        processed_text = re.sub(r'\s*--\s*', r'<hr>', processed_text)
        
        # 处理标题（以#开头的行）
        processed_text = re.sub(r'^(#+)\s+(.*?)$', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>', processed_text, flags=re.MULTILINE)
        
        # 处理列表（以-开头的行）
        processed_text = re.sub(r'^- (.*?)$', r'<li>\1</li>', processed_text, flags=re.MULTILINE)
        
        # 处理有序列表（数字开头的行）
        processed_text = re.sub(r'^(\d+)\. (.*?)$', r'<li>\1. \2</li>', processed_text, flags=re.MULTILINE)
        
        # 将连续的<li>元素包装在<ul>或<ol>中
        if '<li>' in processed_text:
            # 简单检测是否有数字列表
            has_number_list = bool(re.search(r'<li>\d+\.', processed_text))
            list_tag = 'ol' if has_number_list else 'ul'
            
            # 将连续的<li>元素包装在列表标签中
            li_pattern = r'(<li>.*?</li>\s*?)+'
            processed_text = re.sub(li_pattern, lambda m: f'<{list_tag}>{m.group(0)}</{list_tag}>', processed_text)
        
        # 处理段落 - 将连续的文本行分成段落
        if '<p>' not in processed_text:
            paragraphs = re.split(r'\n\s*\n', processed_text)
            processed_text = ''.join([f'<p>{p}</p>' if not p.strip().startswith('<') else p for p in paragraphs if p.strip()])
        
        # 最后使用markdown-it处理任何剩余的Markdown语法
        html = md.render(processed_text)
        
        return html
    except Exception as e:
        logger.error(f"解析Markdown内容时出错: {str(e)}")
        # 出错时返回原始内容
        return text
        
def parse_analysis_data(analysis_data):
    """
    解析整个分析数据对象中的所有Markdown内容
    
    Args:
        analysis_data: 包含分析内容的字典
        
    Returns:
        dict: 解析后的分析数据
    """
    if not analysis_data:
        return {}
        
    try:
        # 创建解析后的数据副本
        parsed_data = {}
        
        # 遍历所有键值对
        for key, value in analysis_data.items():
            if isinstance(value, str):
                # 如果值是字符串，尝试解析Markdown
                parsed_data[key] = parse_markdown(value)
            elif isinstance(value, dict):
                # 如果值是字典，递归解析
                parsed_data[key] = parse_analysis_data(value)
            elif isinstance(value, list):
                # 如果值是列表，处理列表中的每个项目
                parsed_list = []
                for item in value:
                    if isinstance(item, str):
                        parsed_list.append(parse_markdown(item))
                    elif isinstance(item, dict):
                        parsed_list.append(parse_analysis_data(item))
                    else:
                        parsed_list.append(item)
                parsed_data[key] = parsed_list
            else:
                # 其他类型直接复制
                parsed_data[key] = value
                
        return parsed_data
    except Exception as e:
        logger.error(f"解析分析数据时出错: {str(e)}")
        # 出错时返回原始数据
        return analysis_data 