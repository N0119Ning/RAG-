## Why

风景园林设计师/学生在日常工作中需要频繁查询国标/行标中的设计参数（绿地率、道路宽度、无障碍要求等）。传统方式是翻阅几十本 PDF 手动搜索，一条参数可能花 10-15 分钟。通用 LLM 有幻觉风险（编造条款号）、训练数据过时、无法精确定位"第X.X条"。需要一套基于 RAG 的智能规范查询系统。

## What Changes

- **新增** Streamlit 问答界面：自然语言提问 → 精确规范引用（规范名+条款号+原文）
- **新增** PDF 解析管道：PyMuPDF 文本提取 + PaddleOCR 缺字页面兜底
- **新增** 条款切分模块：按条款号（3.1.2、第4.0.2条等）结构化切分
- **新增** RAG 检索引擎：BGE-M3 中文向量化 + ChromaDB 持久化 + 混合检索（向量 50% + jieba 关键词 50%）
- **新增** LLM 回答生成：DeepSeek API 生成带精确引用的回答
- **新增** 8 份国标/行标 PDF 知识库（GB 50180、GB 50016、GB 50420、CJJ 82 等）

## Capabilities

### New Capabilities
- `pdf-parsing`: PDF 规范文档解析，文本提取 + OCR 兜底
- `clause-chunking`: 按条款号结构化切分，强条自动标注
- `rag-retrieval`: BGE-M3 + ChromaDB 混合检索（语义+关键词）
- `answer-generation`: LLM 生成带精确引用的回答（规范名+条款号+原文）
- `knowledge-base-management`: ChromaDB 向量库持久化，支持增量导入

### Modified Capabilities
- 无

## Impact

- 受影响的文件：`app.py`, `rag/pdf_parser.py`, `rag/clause_chunker.py`, `rag/embedder.py`, `rag/retriever.py`, `rag/knowledge_base.py`, `utils/llm_client.py`, `utils/answer_generator.py`
- 依赖：DeepSeek API, ChromaDB, BGE-M3 (SentenceTransformer), PaddleOCR (备选), jieba
- 数据：8 份国标/行标 PDF (114MB)
