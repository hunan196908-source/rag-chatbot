# 基于 LangChain 的 RAG 智能客服知识库系统

一个完整的 RAG（Retrieval-Augmented Generation，检索增强生成）小项目：先把自己提供的资料建成本地知识库，再通过网页用自然语言提问，系统会先从知识库检索相关片段，交给大模型"开卷"组织出答案。支持多轮对话记忆、流式输出和上传内容去重。

## 功能特性

- **知识入库**：网页上传 `.txt` 文档 → 自动预览 → 写入向量数据库
- **MD5 去重**：相同内容重复上传会自动跳过，不重复入库
- **智能分段**：长文本按标点切成 500 字的小块（重叠 50 字），短文本整段入库
- **语义检索**：基于向量相似度，从知识库找出与问题最相关的片段
- **RAG 问答**：把检索到的资料塞进提示词，让大模型依据你的资料作答，减少幻觉
- **多轮记忆**：每个会话的问答历史保存在本地文件，能记住上下文、主动追问
- **流式输出**：回答逐字显示，体验接近真人聊天

## 技术栈

| 层次    | 技术                                    |
| ----- | ------------------------------------- |
| 网页界面  | Streamlit                             |
| 编排框架  | LangChain / LangChain Core（LCEL 链式调用） |
| 向量数据库 | Chroma（本地持久化）                         |
| 嵌入模型  | 阿里 DashScope `text-embedding-v4`      |
| 对话大模型 | 阿里通义千问 `qwen-max`（通过 DashScope）       |
| 运行环境  | Python 3.11（venv 虚拟环境）                |

## 项目结构

| 文件                     | 作用                                       |
| ---------------------- | ---------------------------------------- |
| `config_data.py`       | 配置中心：模型名、分段参数、检索条数、会话 ID                 |
| `app_file_uploader.py` | 页面一：上传 txt → 预览 → 存入知识库                  |
| `knowledge_base.py`    | 入库引擎：MD5 去重、文本分段、调用嵌入模型、写入 Chroma        |
| `vector_stores.py`     | 向量库封装：连接 Chroma，提供 `get_retriever()` 检索器 |
| `rag.py`               | 核心大脑：串联「检索 → 组织提示词 → 大模型」，接上多轮历史         |
| `file_history.py`      | 记忆存储：把每个会话的问答记录存成文件，实现多轮对话               |
| `app.py`               | 页面二：智能客服聊天界面，流式输出                        |

运行时还会生成以下**数据目录**（不建议提交到 Git）：

| 路径              | 内容                        |
| --------------- | ------------------------- |
| `chroma_db/`    | Chroma 向量库持久化数据           |
| `md5.text`      | 已入库内容的 MD5 记录，用于去重        |
| `data/`         | 数据目录                      |
| `path_history/` | 各会话的问答历史（文件名即 session_id） |
| `__pycache__/`  | Python 字节码缓存              |

## 快速开始

### 1. 准备环境

项目依赖安装在一个虚拟环境中（位于项目上一级目录）：

```powershell
cd "C:\Users\hun\Desktop\ai agent"
.venv\Scripts\activate
cd RAG
```

激活后命令行前会出现 `(.venv)` 字样。若还没有虚拟环境或缺少依赖：

```powershell
python -m venv .venv
.venv\Scripts\activate
cd RAG
python -m pip install langchain-community langchain-chroma langchain-text-splitters langchain-core dashscope streamlit
```

### 2. 配置 API Key

项目调用阿里 DashScope，需要设置环境变量 `DASHSCOPE_API_KEY`：

```powershell
# 仅当前会话生效
$env:DASHSCOPE_API_KEY = "你的API_KEY"
```

或在 Windows 系统环境变量中永久添加（此电脑上已配置，可跳过）。

### 3. 启动页面

```powershell
# 页面一：知识库更新（上传资料）
python -m streamlit run app_file_uploader.py

# 页面二：智能客服（提问问答），另开一个终端
python -m streamlit run app.py
```

> 用 `python -m streamlit run` 而不是直接 `streamlit run`，可避免系统 PATH 找不到 streamlit 命令的问题。

### 4. 命令行直接测试

```powershell
python knowledge_base.py   # 测试知识入库
python vector_stores.py    # 测试向量检索
python rag.py              # 测试一次完整问答
```

## 使用说明

1. 启动「知识数据库更新」页面，上传一个 `.txt` 文件（例如服装尺码表），页面会显示文件名、大小和内容预览，并提示入库结果。
2. 启动「智能客服」页面，在底部输入框提问，例如"体重180，尺码推荐"，AI 会流式给出依据你上传资料的回答，并可能主动追问。
3. 对话历史按 `session_id`（默认 `user_001`）保存，刷新页面后仍记得之前的对话。

## 工作原理

```
上传文档 → MD5 去重 → 文本分段 → DashScope 嵌入 → 存入 Chroma
                                                        ↓
用户提问 → 向量检索相关片段 → 拼进提示词(含历史对话) → qwen-max → 流式回答
```

关键点：大模型本身不会去翻知识库，它只拿到「用户的提问 + 检索器挑出的参考资料片段 + 历史对话」，再由 LCEL 链组织提示词、调用模型、解析输出。检索器负责"开卷找资料"，大模型负责"读懂并用人话讲出来"。

## 配置说明（`config_data.py`）

| 配置项                            | 默认值                 | 说明                             |
| ------------------------------ | ------------------- | ------------------------------ |
| `embedding_model`              | `text-embedding-v4` | 嵌入模型名（注意是连字符，不是下划线）            |
| `chat_model_name`              | `qwen-max`          | 对话模型名（`qwen3-max` 在当前账号会报 404） |
| `chunk_size` / `chunk_overlap` | `500` / `50`        | 分段大小与重叠，重叠必须小于分段大小             |
| `max_split_char_number`        | `1000`              | 超过此长度才分段，否则整段入库                |
| `separators`                   | 中文标点列表              | 分段时优先按这些标点切分                   |
| `similarity_threshold`         | `1`                 | 检索返回的文档数量 k                    |
| `session_config`               | `user_001`          | 当前会话 ID，决定读写哪份对话历史             |

## 注意事项

- **必须用虚拟环境运行**：系统 Python 未安装这些依赖，直接 `python xxx.py` 会报 `ModuleNotFoundError`。
- **依赖相对路径**：配置里的路径都是相对路径（如 `./chroma_db`），请在 `RAG` 目录下启动程序。
- **弃用警告可忽略**：`langchain-community` 和 `RunnableWithMessageHistory` 会打印 DeprecationWarning，不影响运行。
- **重置知识库**：删除 `chroma_db/` 和 `md5.text` 后重新启动即可清空。
- **数据文件勿公开**：`chroma_db/`、`data/`、`path_history/`、`md5.text` 是你的业务数据和隐私内容，上传 GitHub 前请用 `.gitignore` 排除。
