import requests
import sys
import os
import webbrowser
from urllib.parse import urljoin

def test_bazi_pdf_api(result_id="RES1747577000978"):
    """测试八字PDF API接口"""
    
    print(f"测试八字命理PDF下载API，结果ID: {result_id}")
    
    # 设置基础URL
    base_url = "http://localhost:5000"
    
    # API路径
    api_path = f"/api/bazi/pdf/{result_id}" 
    
    # 完整的请求URL
    request_url = urljoin(base_url, api_path)
    print(f"请求URL: {request_url}")
    
    # 设置请求头
    headers = {
        "Authorization": "Bearer test-token"
    }
    
    # 发送请求
    try:
        print("发送请求...")
        response = requests.get(request_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # 检查内容类型
            content_type = response.headers.get('Content-Type', '')
            print(f"响应内容类型: {content_type}")
            
            if 'application/pdf' in content_type:
                # 保存PDF到本地
                output_path = os.path.join("pdfs", f"test_download_{result_id}.pdf")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                print(f"保存PDF到: {output_path}")
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"PDF下载成功: {output_path}")
                print(f"PDF文件大小: {os.path.getsize(output_path)} 字节")
                
                # 尝试打开PDF
                print("尝试打开PDF...")
                webbrowser.open(output_path)
                
                return True
            elif 'application/json' in content_type:
                # 显示API返回的JSON
                print("API返回JSON:")
                print(response.json())
                return False
            else:
                print(f"异常的响应内容类型: {content_type}")
                print(f"响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"请求过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 如果提供了命令行参数，使用参数作为结果ID
    if len(sys.argv) > 1:
        test_bazi_pdf_api(sys.argv[1])
    else:
        # 否则使用默认ID
        test_bazi_pdf_api() 