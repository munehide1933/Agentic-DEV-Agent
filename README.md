# Meta-Agent Development System

一个基于多角色协作架构的AI智能体开发系统，用于加速软件开发流程。

## 🌟 核心特性

- **多角色协作架构**: 6个专业角色（架构师、后端、前端、AI工程师、安全审查、PM）协同工作
- **标准化工作流**: 6阶段开发流程（需求理解 → 架构设计 → RAG规划 → 实现 → 安全审查 → 交付）
- **RAG增强**: 基于Qdrant的向量检索，支持项目代码上下文理解
- **代码修改协议**: 安全、可追溯的代码生成和修改
- **安全审查**: 自动化安全漏洞检测
- **对话历史管理**: SQLite持久化存储

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI
- **LLM**: Azure OpenAI (GPT-4)
- **向量数据库**: Qdrant
- **关系数据库**: SQLite
- **ORM**: SQLAlchemy

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **状态管理**: Zustand
- **样式**: TailwindCSS
- **Markdown渲染**: react-markdown
- **代码高亮**: react-syntax-highlighter

## 📋 系统要求

- Python 3.10+
- Node.js 18+
- Windows 10 或 Ubuntu 24.04 LTS
- 8GB+ RAM
- Azure OpenAI API访问权限

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd meta-agent-system
2. 一键安装
Windows:
bashCopypython setup.py
Linux:
bashCopypython3 setup.py
3. 配置环境变量
编辑根目录下的 .env 文件，填入你的 Azure OpenAI 凭证：
envCopyAZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

SECRET_KEY=your-secret-key-change-in-production
4. 启动系统
Windows:
bashCopyrun_windows.bat
Linux:
bashCopy./run_linux.sh
5. 访问应用

前端界面: http://localhost:5173
后端API: http://localhost:8000
API文档: http://localhost:8000/docs

📖 使用指南
创建项目

点击左侧边栏的 "+" 按钮
输入项目名称和描述
点击 "Create Project"

上传代码文件

选择一个项目
点击聊天输入框左侧的📎图标
选择代码文件（支持 .py, .js, .ts, .java, .go, .md 等）
系统会自动进行语义分析和向量化

开始对话
直接在输入框中描述你的需求，例如：
Copy我想开发一个用户认证系统，包含注册、登录、JWT token管理功能，
使用 FastAPI + SQLAlchemy + PostgreSQL
系统会自动：

分析需求
设计架构
生成完整代码
进行安全审查
提供部署建议

RAG检索
上传项目文件后，系统会自动：

分块处理代码（chunk size: 1000 tokens）
生成embeddings（text-embedding-3-large）
存储到Qdrant向量数据库
在对话时自动检索相关上下文

🔧 项目结构
Copymeta-agent-system/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心引擎（工作流、角色、安全）
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务服务（LLM、RAG、向量）
│   │   └── main.py         # FastAPI主应用
│   └── requirements.txt
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── stores/        # Zustand状态管理
│   │   ├── services/      # API服务
│   │   └── types/         # TypeScript类型
│   └── package.json
├── data/                   # 数据目录
│   ├── qdrant/            # 向量数据库
│   ├── sqlite/            # SQLite数据库
│   └── uploads/           # 上传文件
├── setup.py               # 安装脚本
├── run_windows.bat        # Windows启动脚本
├── run_linux.sh           # Linux启动脚本
└── README.md
🛡️ 安全特性

代码安全扫描: 自动检测危险模式（eval, exec, SQL注入等）
API密钥保护: 使用环境变量管理敏感信息
文件系统隔离: 限制代码修改范围
输入验证: Pydantic schema验证
CORS配置: 限制跨域请求

📊 数据持久化
SQLite数据库

projects: 项目信息
conversations: 对话记录
messages: 消息历史
knowledge_files: 文件元数据

Qdrant向量数据库

collection: meta_agent_knowledge
embedding dimension: 3072
distance metric: Cosine

🔍 API 文档
启动后访问 http://localhost:8000/docs 查看完整的API文档（Swagger UI）。
主要端点

POST /api/chat/message - 发送消息
POST /api/projects - 创建项目
GET /api/projects - 获取项目列表
POST /api/projects/{id}/upload-file - 上传文件
POST /api/knowledge/search - 搜索知识库

🐛 故障排查
后端无法启动

检查 .env 文件是否正确配置
确认 Azure OpenAI 凭证有效
查看日志：backend/logs/app.log

Qdrant连接失败
系统使用本地嵌入模式，无需额外安装Qdrant服务。数据存储在 data/qdrant/ 目录。
前端无法连接后端

确认后端已启动（http://localhost:8000/health）
检查CORS配置（.env 中的 CORS_ORIGINS）
查看浏览器控制台错误

📝 开发指南
添加新的角色
编辑 backend/app/core/personas.py：
pythonCopyPersonaRole.NEW_ROLE: """You are a new role..."""
扩展工作流阶段
编辑 backend/app/core/workflow_engine.py：
pythonCopyclass WorkflowPhase(str, Enum):
    NEW_PHASE = "new_phase"
自定义代码修改规则
编辑 backend/app/core/code_modifier.py
🤝 贡献
欢迎提交 Issue 和 Pull Request！
📄 许可证
MIT License
🙏 致谢

Azure OpenAI
Qdrant
FastAPI
React


Enjoy building with Meta-Agent! 🚀
Copy
---

## 完整部署清单

✅ **后端代码** (完整)
- 配置管理
- 数据库模型
- 核心引擎（工作流、角色、代码修改、安全审查）
- LLM服务
- RAG服务
- 向量服务
- 对话管理服务
- API路由

✅ **前端代码** (完整)
- TypeScript类型定义
- Zustand状态管理
- API服务封装
- React组件（布局、聊天界面、消息列表、输入区域）
- TailwindCSS样式

✅ **部署脚本**
- Windows启动脚本
- Linux启动脚本
- Python安装脚本
- 完整README文档

---

## 🎯 Next Steps

**请按以下步骤部署：**

1. **创建项目目录结构** 并复制所有代码文件
2. **运行安装脚本**: `python setup.py`
3. **配置 .env 文件** 添加 Azure OpenAI 凭证
4. **启动系统**:
   - Windows: `run_windows.bat`
   - Linux: `./run_linux.sh`
5. **访问** http://localhost:5173 开始使用

---

**Security Review:**

⚠️ **生产环境注意事项**:
1. 更改 `SECRET_KEY` 为强随机字符串
2. 启用 HTTPS（使用 Nginx + Let's Encrypt）
3. 限制文件上传大小（已设置10MB）
4. 定期备份 SQLite 和 Qdrant 数据
5. 监控 API 调用成本
6. 实施速率限制（FastAPI Limiter）

---

**Optional Enhancements:**

1. Docker 部署配置
2. 用户认证系统
3. 多项目并行支持
4. 代码差异可视化
5. 自动化测试生成
6. CI/CD集成
