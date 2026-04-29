# AI-新闻系统

> 本项目由 [Trae IDE](https://www.trae.ai/) 开发完成，是一款基于 AI 能力的智能新闻管理系统。

## 项目简介

AI-新闻系统是一个集新闻采集、编辑、发布于一体的智能化管理平台。系统支持多种新闻采集方式（新闻API、大语言模型生成、网页爬取），并提供完善的新闻管理、分类管理和菜单配置功能。

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Vue Composition API
- **路由**: Vue Router
- **HTTP 客户端**: Axios

### 后端
- **框架**: FastAPI (Python 3.12)
- **服务器**: Uvicorn
- **数据库**: MySQL (PyMySQL)
- **网页解析**: BeautifulSoup4 + lxml
- **爬虫引擎**: Playwright (支持动态渲染)
- **RSS 解析**: feedparser

## 项目结构

```
news/
├── backend/                    # 后端服务
│   ├── api.py                  # FastAPI 路由入口
│   ├── main.py                 # 应用启动入口
│   ├── requirements.txt        # Python 依赖
│   ├── .env                    # 环境变量配置
│   ├── db/                     # 数据库模块
│   │   ├── conf/               # 数据库配置与初始化
│   │   ├── sql/                # SQL 脚本
│   │   │   ├── schema.sql      # 表结构定义
│   │   │   ├── init_data.sql   # 初始数据
│   │   │   └── add_llm_config.sql  # LLM 配置补充
│   │   ├── utils.py            # 数据库工具函数
│   │   └── enums.py            # 枚举定义
│   ├── service/                # 业务服务层
│   │   ├── spider.py           # 爬虫服务（网页采集、API新闻）
│   │   ├── llm.py              # 大语言模型服务
│   │   ├── news.py             # 新闻管理服务
│   │   ├── category.py         # 分类管理服务
│   │   ├── menu.py             # 菜单管理服务
│   │   ├── config.py           # 系统配置服务
│   │   └── user.py             # 用户管理服务
│   └── prompts/                # 提示词文件
│       └── system_prompt.md    # LLM 系统提示词
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── main.ts             # 应用入口
│   │   ├── App.vue             # 根组件
│   │   ├── components/         # 公共组件
│   │   │   ├── LLMChat.vue     # AI 聊天组件
│   │   │   ├── HeaderNav.vue   # 顶部导航
│   │   │   ├── SidebarMenu.vue # 侧边菜单
│   │   │   ├── NewsList.vue    # 新闻列表
│   │   │   └── IconSelector.vue# 图标选择器
│   │   ├── composables/        # 组合式函数
│   │   │   ├── useMessage.ts   # 全局消息提示
│   │   │   └── usePageIcon.ts  # 页面图标
│   │   ├── views/              # 页面视图
│   │   ├── router/             # 路由配置
│   │   ├── utils/              # 工具函数
│   │   └── assets/             # 静态资源
│   └── package.json
```

## 功能模块

### 新闻汇总
系统首页，展示各类新闻的汇总信息，支持按分类快速浏览。

### 新闻管理

#### 新闻分类
- 管理新闻分类（国内新闻、国际新闻等）
- 支持分类的增删改查
- 可配置分类图标、排序和状态

#### 新闻API
- 集成多个免费新闻源：
  - **60秒新闻**: 每日60秒新闻速览
  - **CCTV新闻**: 央视官方RSS
  - **新浪新闻**: 新浪滚动新闻
  - **百度热搜**: 实时热搜榜单

#### 大语言模型
- 类 DeepSeek 风格的 AI 聊天界面
- 内置专业新闻从业者提示词
- 支持多轮对话和上下文记忆
- 提供 **复制**、**重新生成**、**采集新闻** 功能
- 自动将 AI 生成的内容按格式拆分为多条新闻
- 兼容 OpenAI API 格式，支持自定义模型

#### 网页爬取
- 支持主流新闻网站内容采集（新华网、中新网、人民网、网易、腾讯、央视等）
- 静态 HTML 解析 + Playwright 动态渲染双引擎
- 多策略正文提取算法
- 自动过滤广告和无关内容

#### 新闻采集
- 统一入口，支持三种采集方式：
  1. 新闻API采集
  2. 大语言模型生成
  3. 网页爬取

#### 撰写新闻
- 手动编写新闻稿件
- 支持选择分类和来源
- 可保存为草稿或直接发布

#### 草稿箱
- 管理未发布的新闻草稿
- 支持编辑、发布、删除操作
- 来源列过长自动省略显示

#### 已发布
- 查看已发布的新闻列表
- 支持撤销发布操作
- 支持批量撤销发布

### 用户管理

#### 用户列表
- 管理系统用户
- 查看用户信息和状态

### 系统设置

#### 基本设置
- 配置系统名称和图标
- 设置登录页背景
- 配置 LLM 参数（API Key、Base URL、模型名称）

#### 菜单管理
- 可视化菜单树管理
- 支持多级菜单配置
- 可设置菜单图标、路径、排序和显示状态

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 18+
- MySQL 5.7+

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置环境变量
# 编辑 .env 文件，配置数据库连接信息

# 启动服务
python main.py
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 配置说明

### 数据库配置
编辑 `backend/.env` 文件：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=ai_news
```

### LLM 配置
在系统设置中配置：
- **API Key**: 兼容 OpenAI 格式的密钥
- **Base URL**: API 基础地址（如 `https://api.openai.com/v1`）
- **模型名称**: 使用的模型（如 `gpt-3.5-turbo`）

### 提示词配置
编辑 `backend/prompts/system_prompt.md` 文件可自定义 AI 助手的角色设定和输出格式。

## 许可证

MIT License
