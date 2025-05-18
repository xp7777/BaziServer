#!/bin/bash

# 检查Python环境
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到python3，请安装Python 3.8+"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null
then
    echo "错误: 未找到pip3，请安装pip"
    exit 1
fi

# 检查MongoDB
mongo_status=$(systemctl is-active mongod 2>/dev/null)
if [[ "$mongo_status" != "active" ]]; then
    echo "警告: MongoDB服务可能未运行，请确保MongoDB已启动"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查sxtwl包安装情况
echo "检查sxtwl包安装情况..."
python -c "import sxtwl" &> /dev/null
if [ $? -ne 0 ]; then
    echo "检测到sxtwl包未正确安装，尝试安装..."
    python install_sxtwl.py
    if [ $? -ne 0 ]; then
        echo "警告: sxtwl包安装失败，请查看SXTWL_README.md获取手动安装指南"
    else
        echo "sxtwl包已成功安装"
    fi
fi

# 创建PDF目录
mkdir -p pdfs

# 检查环境变量配置
if [ ! -f ".env" ]; then
    echo "未找到.env文件，正在从示例创建..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env文件已创建，请编辑其中的配置参数"
    else
        echo "错误: 未找到.env.example文件"
        exit 1
    fi
fi

# WeasyPrint信息
echo "==========================================================="
echo "系统使用WeasyPrint生成PDF，无需安装外部依赖"
echo "如果PDF生成出现问题，请检查WeasyPrint库是否正确安装"
echo "==========================================================="
echo "系统使用sxtwl包计算农历和干支"
echo "如果遇到sxtwl相关问题，请查看SXTWL_README.md获取帮助"
echo "==========================================================="

# 启动应用
echo "启动八字命理AI人生指导系统..."
python app.py 