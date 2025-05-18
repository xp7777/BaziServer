@echo off
echo ===========================================
echo 八字命理AI指导系统 - 前端修复和启动脚本
echo ===========================================

echo 1. 清除缓存...
call npm cache clean --force

echo 2. 安装依赖...
call npm install

echo 3. 启动开发服务器...
call npm run serve

pause 