import os
from weasyprint import HTML

def test_pdf_generation():
    # 创建简单HTML内容
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>测试PDF生成</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            h1 { color: #1989fa; }
            p { line-height: 1.5; }
        </style>
    </head>
    <body>
        <h1>WeasyPrint测试</h1>
        <p>这是使用WeasyPrint生成的测试PDF文档。</p>
        <p>如果您看到这个文件，说明PDF生成功能正常工作！</p>
    </body>
    </html>
    """
    
    # 确保pdf目录存在
    pdf_dir = "pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 生成PDF路径
    pdf_path = os.path.join(pdf_dir, "test.pdf")
    
    try:
        # 使用WeasyPrint生成PDF
        print(f"正在生成测试PDF: {pdf_path}")
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"PDF生成成功: {pdf_path}")
        return True
    except Exception as e:
        print(f"生成PDF时出错: {str(e)}")
        return False

if __name__ == "__main__":
    test_pdf_generation() 