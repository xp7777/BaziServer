# 捭阖学宫网站 + 八字命理AI人生指导

## 项目说明

本项目整合了两个功能：
1. 捭阖学宫文化主题网站（首页）
2. 八字命理AI人生指导服务（功能页）

## 技术栈

- 前端框架: Vue 3
- UI组件库: Vant UI
- 路由: Vue Router
- 状态管理: Pinia
- 样式: 自定义CSS (类Tailwind风格)

## 目录结构

```
frontend/
├── public/          # 静态资源
├── src/
│   ├── api/         # API接口
│   ├── assets/      # 图片资源
│   │   ├── banner1.png
│   │   ├── banner2.png
│   │   ├── banner3.png
│   │   ├── banner4.png
│   │   └── logo.png
│   ├── components/  # Vue组件
│   │   ├── NavComponent.vue      # 导航组件
│   │   ├── HeroBanner.vue        # 轮播图组件
│   │   ├── SectionComponent.vue  # 章节组件
│   │   ├── AboutSection.vue      # 关于我们组件
│   │   └── BackToTop.vue         # 回到顶部组件
│   ├── App.vue      # 主应用组件
│   ├── App.css      # 全局样式
│   ├── Home.vue     # 捭阖学宫首页
│   ├── BaziService.vue  # 八字命理服务页面
│   ├── main.js      # 入口文件
│   └── router.js    # 路由配置
└── package.json     # 项目配置
```

## 页面说明

1. **首页 (/)**: 捭阖学宫文化主题网站，包含轮播图、关于我们、国学教育、人生指导、在线课程和联系我们等板块。
2. **八字命理服务页 (/bazi-service)**: 八字命理AI人生指导服务表单页面。
3. **支付页 (/payment)**: 订单支付页面。
4. **结果页 (/result/:id)**: 八字分析结果展示页面。
5. **用户中心 (/user)**: 用户个人中心页面。
6. **登录页 (/login)**: 用户登录页面。

## 如何启动

1. 安装依赖:
```bash
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

3. 构建生产版本:
```bash
npm run build
```

## 路由导航

- 首页访问: `http://localhost:端口号/`
- 八字服务页访问: `http://localhost:端口号/bazi-service`
- 在首页点击"人生指导"板块中的"点击进入"按钮，会跳转到八字服务页面

## 注意事项

1. 首页不显示底部导航栏，其他页面会显示
2. 首页使用了响应式设计，适配手机、平板和桌面设备
3. 所有图片资源已放置在assets目录下
4. 如需修改首页内容，请编辑相应的Vue组件 