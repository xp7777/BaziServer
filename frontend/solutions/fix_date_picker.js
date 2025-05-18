#!/usr/bin/env node

/**
 * 日期选择器修复脚本
 * 
 * 这个脚本会：
 * 1. 降级Vant版本到3.4.6
 * 2. 修改Home.vue中的组件使用方式
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const homeVuePath = path.join(__dirname, 'Home.vue');

console.log('开始修复日期选择器问题...');

// 步骤1: 降级Vant版本
console.log('\n步骤1: 降级Vant版本到3.4.6');
try {
  console.log('卸载当前Vant版本...');
  execSync('npm uninstall vant', { stdio: 'inherit' });
  
  console.log('安装Vant 3.4.6...');
  execSync('npm install vant@3.4.6', { stdio: 'inherit' });
  
  console.log('✅ Vant版本已降级');
} catch (error) {
  console.error('❌ Vant版本降级失败:', error.message);
  process.exit(1);
}

// 步骤2: 修改Home.vue文件
console.log('\n步骤2: 修改Home.vue中的组件使用方式');
try {
  if (!fs.existsSync(homeVuePath)) {
    console.error('❌ 找不到Home.vue文件');
    process.exit(1);
  }
  
  // 备份原文件
  const backupPath = homeVuePath + '.bak';
  fs.copyFileSync(homeVuePath, backupPath);
  console.log(`已备份原文件到: ${backupPath}`);
  
  // 读取文件内容
  let content = fs.readFileSync(homeVuePath, 'utf-8');
  
  // 替换popup部分
  content = content.replace(
    /<van-popup[^>]*>[^<]*<van-date-picker[^>]*>/g,
    '<van-popup v-model="showDatePicker" position="bottom">\n          <van-datetime-picker v-model="currentDate" type="date"'
  );
  
  content = content.replace(
    /<van-popup[^>]*>[^<]*<van-picker/g,
    '<van-popup v-model="showTimePicker" position="bottom">\n          <van-picker'
  );
  
  // 替换字段点击处理函数
  content = content.replace(
    /@click="debugDateClick"/g,
    '@click="showDatePicker = true"'
  );
  
  content = content.replace(
    /@click="debugTimeClick"/g,
    '@click="showTimePicker = true"'
  );
  
  // 写入修改后的内容
  fs.writeFileSync(homeVuePath, content);
  console.log('✅ Home.vue文件已更新');
  
} catch (error) {
  console.error('❌ 修改Home.vue文件失败:', error.message);
  process.exit(1);
}

console.log('\n✅ 修复完成! 请运行 "npm run serve" 启动开发服务器'); 