@echo off
echo =============================================
echo 八字命理AI - 应用日期选择器简单替代方案
echo =============================================

echo 1. 备份当前Home.vue文件...
copy Home.vue Home.vue.bak

echo 2. 应用简单替代方案...
copy Home.simple.vue Home.vue

echo 3. 启动开发服务器...
npm run serve

echo.
echo 替代方案已应用！现在使用原生HTML日期选择器替代Vant组件。
echo 如需恢复原方案，请运行: copy Home.vue.bak Home.vue
echo.

pause 