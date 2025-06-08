import requests
import sys

try:
    response = requests.get('http://localhost:5000/api/health')
    print('状态码:', response.status_code)
    print(response.text)
except Exception as e:
    print('错误:', str(e))
    sys.exit(1) 