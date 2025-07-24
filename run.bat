@echo off
echo 启动八字命理AI人生指导系统...

REM 检查Python环境
python --version > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到Python，请安装Python 3.8+
    pause
    exit /b 1
)

REM 检查pip
pip --version > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到pip，请安装pip
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist venv (
    echo 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 检查sxtwl包安装情况
echo 检查sxtwl包安装情况...
python -c "import sxtwl" > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 检测到sxtwl包未正确安装，尝试手动安装...
    pip install sxtwl
    if %ERRORLEVEL% NEQ 0 (
        echo 警告: sxtwl包安装失败，请手动安装或查看文档
    ) else (
        echo sxtwl包已成功安装
    )
)

REM 创建必要目录
if not exist pdfs (
    mkdir pdfs
)
if not exist logs (
    mkdir logs
)
if not exist logs\errors (
    mkdir logs\errors
)

REM 检查环境变量配置
if not exist .env (
    echo 未找到.env文件，正在从示例创建...
    if exist .env.example (
        copy .env.example .env
        echo .env文件已创建，请编辑其中的配置参数
    ) else (
        echo 错误: 未找到.env.example文件
        pause
        exit /b 1
    )
)

echo ===========================================================
echo 系统使用WeasyPrint生成PDF，无需安装外部依赖
echo 如果PDF生成出现问题，请检查WeasyPrint库是否正确安装
echo ===========================================================
echo 日志系统已配置：控制台显示所有日志，文件只记录ERROR级别
echo 错误日志位置: logs\errors\error.log
echo ===========================================================

REM 启动应用
echo 启动八字命理AI人生指导系统...
python app.py

pause 
