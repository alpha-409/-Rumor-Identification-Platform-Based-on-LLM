# 基于LLM的谣言识别平台

基于大语言模型的微博谣言识别和舆情分析平台。实时获取微博热门话题，进行谣言识别和舆情分析。

## 项目结构

```
.
├── app.py              # Flask后端服务
├── weibo_crawler.py    # 微博爬虫模块
├── requirements.txt    # Python依赖
├── frontend/          # Vue.js前端
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   │   ├── TopicItem.vue    # 话题项组件
│   │   │   └── TopicList.vue    # 话题列表组件
│   │   ├── services/    # API服务
│   │   │   └── api.js   # API接口封装
│   │   ├── App.vue      # 根组件
│   │   └── main.js      # 入口文件
│   ├── index.html       # HTML模板
│   ├── vite.config.js   # Vite配置
│   └── package.json     # 前端依赖
├── data/              # 数据存储目录
│   └── weibo_hot_topics.csv  # 微博话题数据
├── cache/             # 缓存目录
│   └── images/        # 图片缓存
└── static/           # 静态资源目录
```

## 功能特性

- 实时获取微博热门话题数据
- 自动每10秒更新一次数据
- 图片缓存和代理加载
- 数据自动去重并保存至CSV
- 支持手动/自动数据刷新
- 显示话题详细信息（用户信息、图片、统计数据等）

## 技术栈

### 前端
- Vue 3 (组合式API)
- Vite
- Axios

### 后端
- Python
- Flask
- Flask-CORS

## 开发环境设置

1. 安装后端依赖：
```bash
pip install -r requirements.txt
```

2. 安装前端依赖：
```bash
cd frontend
npm install
```

## 运行项目

1. 启动Flask后端服务：
```bash
python app.py
```
后端服务将在 http://localhost:5000 运行

2. 启动Vue开发服务器：
```bash
cd frontend
npm run dev
```
前端页面将在 http://localhost:5173 运行

## 项目配置

### 后端配置

- 图片缓存配置（在app.py中）：
  - `CACHE_DIR`: 缓存目录路径
  - `CACHE_TIMEOUT`: 缓存过期时间（秒）
  - `MAX_CACHE_SIZE`: 最大缓存大小

### 前端配置

- API代理配置（在vite.config.js中）：
  - 开发环境下自动代理/api请求到后端服务

## 数据存储

- 话题数据以CSV格式存储在data目录
- 图片缓存存储在cache/images目录
- 自动清理过期和超量的缓存文件

## 浏览器兼容性

- 支持所有现代浏览器
- 推荐使用Chrome、Firefox、Safari最新版本
