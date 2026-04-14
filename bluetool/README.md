# BlueTool - AI 自动化测试用例生成工具

BlueTool 是一款基于 AI 的自动化测试用例生成工具，能够将人工软件测试的完整思路通过 AI 自动化复现，实现从「需求文档」一键生成「专业测试点 + 标准测试用例」。

## 核心功能

1. **需求文档上传** - 支持 Markdown、Word、PDF、TXT 等多种格式
2. **智能文档解析** - 自动识别文档中的文本、表格和图片内容
3. **智能文档拆分** - 自动识别大文档，按功能模块智能拆分
4. **AI 测试点分析** - 调用大模型自动提取各类测试点，支持表格和图片内容识别
5. **测试点编辑** - 可视化编辑界面，支持增删改
6. **标准用例生成** - 基于测试点生成完整格式测试用例，符合《测试用例生成规范》
7. **结果导出** - 支持 JSON、Markdown、Excel 等多种格式导出

## 技术栈

### 前端
- Vue 3 + Vite
- Element Plus UI 组件库
- Vue Router
- Axios

### 后端
- Flask (Python 3)
- Flask-CORS
- LangChain + OpenAI API
- python-docx / PyPDF2 (文档解析)
- openpyxl (Excel 导出)

## 快速开始

### 1. 进入项目目录

```bash
cd /Users/xujiahui/Documents/trae_projects/bluetool
```

### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，用于 AI 功能）
export OPENAI_API_KEY="your-api-key-here"
# 或 export DEEPSEEK_API_KEY="your-deepseek-key"

# 启动服务
python app.py
```

后端服务默认运行在 http://localhost:5000

### 3. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务默认运行在 http://localhost:5173 或其他可用端口

### 4. 访问应用

打开浏览器访问前端服务地址（如 http://localhost:5173）

## 使用流程

1. **上传文档** - 在「文档上传」页面上传需求文档（.md/.docx/.pdf/.txt）
2. **解析文档** - 系统自动解析文档，提取文本、表格和图片内容，并拆分文档为多个模块
3. **生成测试点** - 点击「AI 生成测试点」，系统根据文档内容动态生成测试点
4. **编辑测试点** - 在「测试点管理」页面查看、编辑、增删测试点
5. **生成测试用例** - 点击「生成测试用例」，系统基于测试点生成标准格式用例
6. **导出结果** - 在「测试用例」页面导出为 JSON、Markdown 或 Excel 格式

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传文档 |
| `/api/parse` | POST | 解析文档（提取文本、表格、图片） |
| `/api/generate-test-points` | POST | 生成测试点（支持表格和图片内容） |
| `/api/generate-test-cases` | POST | 生成测试用例 |
| `/api/history` | GET | 获取历史记录 |
| `/api/export` | POST | 导出用例（JSON/Markdown/Excel） |
| `/api/download-excel/<filename>` | GET | 下载 Excel 文件 |

## 配置 AI 模型

在 `backend/app.py` 中可以配置不同的 AI 模型：

```python
# 使用 OpenAI
export OPENAI_API_KEY="your-key"

# 或使用 DeepSeek
export DEEPSEEK_API_KEY="your-key"
```

如果不配置 API Key，系统会使用基于文档内容的测试点生成算法。

## 测试用例生成规范

生成的测试用例严格遵循《测试用例生成规范》，包含以下字段：
- **case_id**: 用例编号（如 TC-001）
- **title**: 测试标题（不超过 30 字）
- **module**: 所属模块
- **preconditions**: 前置条件
- **steps**: 测试步骤
- **expected_results**: 预期结果
- **priority**: 优先级（高/中/低）
- **involve_side**: 涉及端侧（Web 端）
- **scene**: 场景（正向/异常校验/边界值/权限控制/网络异常）

## 项目结构

```
bluetool/
├── backend/
│   ├── app.py              # Flask 主应用
│   ├── requirements.txt    # Python 依赖
│   ├── uploads/            # 上传文件存储目录
│   └── history.json        # 历史记录文件
├── frontend/
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── Upload.vue  # 文档上传页面
│   │   │   ├── Parse.vue   # 文档解析页面
│   │   │   ├── TestPoints.vue # 测试点管理页面
│   │   │   └── TestCases.vue  # 测试用例页面
│   │   ├── router/         # 路由配置
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── package.json
│   └── vite.config.js
├── 测试用例生成规范.md       # 测试用例生成规范文档
└── README.md
```

## 注意事项

1. 首次运行需要安装前后端依赖
2. 如需使用 AI 功能，需要配置 API Key
3. 上传文件大小限制为 100MB
4. 支持的文档格式：.md, .docx, .pdf, .txt
5. 系统支持识别文档中的表格和图片内容，并据此生成测试点
6. 测试用例导出支持 JSON、Markdown 和 Excel 格式

## License

MIT