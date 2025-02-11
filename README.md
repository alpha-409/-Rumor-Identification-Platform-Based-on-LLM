# 基于LLM的谣言识别和舆情分析平台

一个基于Flask和Vue.js的Web应用，用于实时获取微博热门话题，进行谣言识别和舆情分析。

## 功能特点

- 实时抓取微博热门话题数据
- 自动保存数据至CSV文件
- 实时展示话题热度信息（转发、评论、点赞数）
- 支持定期自动更新数据
- 简洁直观的Web界面

## 技术栈

- Backend: Python/Flask
- Frontend: Vue.js
- 数据存储: CSV
- 数据源: 微博API

## 安装和运行

1. 克隆仓库：
```bash
git clone [repository-url]
cd -Rumor-Identification-Platform-Based-on-LLM
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 访问应用：
打开浏览器访问 http://localhost:5000

## 项目结构

```
.
├── app.py              # Flask应用主文件
├── weibo_crawler.py    # 微博数据爬取模块
├── requirements.txt    # 项目依赖
├── templates/         
│   └── index.html     # Vue.js前端页面
└── data/              # 数据存储目录
    └── *.csv          # 爬取的数据文件
```

## 贡献指南

欢迎提交Pull Request和Issue来帮助改进项目。

## 开发计划

- [ ] 集成LLM进行谣言识别
- [ ] 添加舆情分析功能
- [ ] 实现历史数据查询
- [ ] 添加数据可视化功能
- [ ] 优化数据存储结构
- [ ] 添加用户认证系统

## 许可证

MIT License
