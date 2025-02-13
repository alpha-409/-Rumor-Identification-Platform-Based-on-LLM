# 基于LLM的微博谣言识别平台

## 项目概述
本项目是一个基于微博数据的谣言识别系统，通过采集微博数据，利用大语言模型(LLM)进行谣言识别和分析。系统包含数据采集、数据处理、谣言识别和结果展示等功能模块。

## 技术栈
- Python 3.x
- Flask/Django (Web框架)
- Requests/Scrapy (数据采集)
- Pandas (数据处理)
- LLM模型 (谣言识别)
- HTML/CSS/JS (前端展示)

## 文件结构
```
.
├── app.py                # Web应用主程序
├── weibo_scraper.py      # 微博数据采集脚本
├── requirements.txt      # 依赖包列表
├── weibo_data.csv        # 采集的微博数据
├── templates/            # 前端模板
│   └── index.html        # 主页面
└── README.md             # 项目文档
```

## 主要功能模块
1. 数据采集模块
   - 通过微博API或网页爬虫获取微博数据
   - 数据包括：微博内容、发布时间、用户信息等
   - 数据存储为CSV格式

2. 数据处理模块
   - 数据清洗和预处理
   - 特征提取
   - 数据格式转换

3. 谣言识别模块
   - 基于LLM的谣言检测算法
   - 情感分析
   - 可信度评分

4. 结果展示模块
   - Web界面展示分析结果
   - 可视化图表
   - 谣言预警

## 运行说明
1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行数据采集
```bash
自动运行，请注意，请将
**weibo_scraper.py **
替换为自己的微博的cookie，自行查找资料
```

3. 启动Web应用
```bash
python app.py
```

4. 访问应用
打开浏览器访问 http://localhost:5000

## 数据格式说明
采集的微博数据存储在weibo_data.csv文件中，包含以下字段：
- id: 微博ID
- content: 微博内容
- created_at: 发布时间
- user_id: 用户ID
- user_name: 用户名
- reposts_count: 转发数
- comments_count: 评论数
- attitudes_count: 点赞数
