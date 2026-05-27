## Context

园规通（YuanGuiTong）——风景园林设计规范智能助手。RAG 驱动，精确引用，面向设计师/学生的规范查询工具。当前阶段：MVP，8 份核心国标/行标。

## Goals / Non-Goals

**Goals:**
- 自然语言提问 → 秒级返回精确规范引用（规范名+条款号+原文）
- 检索命中率 > 90%，回答幻觉率 < 2%
- 知识库支持增量导入新规范
- 回答包含精确出处，可追溯验证

**Non-Goals:**
- V2 合规审查引擎（Module 2）暂不实现
- 不支持规范版本对比
- 不支持多用户协作
- 不处理扫描件 PDF（无文本层时依赖 OCR 质量）

## Decisions

| 决策 | 选型 | 备选 | 理由 |
|------|------|------|------|
| 架构模式 | RAG + LLM | 纯 LLM / 纯规则引擎 | RAG 解决精确引用，LLM 解决自然语言交互 |
| Embedding 模型 | BGE-M3 (1024维) | all-MiniLM-L6-v2 / OpenAI | 中文优化，1024维语义表达好 |
| 向量数据库 | ChromaDB | Pinecone / Milvus | 轻量嵌入式，MVP 8 份规范无压力 |
| PDF 解析 | MinerU (magic-pdf CLI) | PyMuPDF / PaddleOCR | 中文多栏排版准确，输出 Markdown 保留结构，自带 OCR 能力 |
| 中文分词 | jieba | 标点切分 | 准确提取关键词，提升混合检索命中率 |
| 混合检索权重 | 向量 50% + 关键词 50% | 70/30 | 规范查询关键词同等重要 |
| 条款切分 | Markdown 标题层级 + 条款号正则 | 固定大小切分 | MinerU 输出 Markdown，标题即条款层级，保留完整性 |

## Risks / Trade-offs

- [检索不准确] → BGE-M3 中文优化 + jieba 分词 + 50/50 混合检索
- [PDF 文本缺失/排版复杂] → MinerU 解析（多栏中文排版准确，自带 OCR）
- [LLM 幻觉] → Prompt 强制引用原文 + 每条回答标注来源
- [知识库扩展性能] → ChromaDB 支持 > 100 份规范后再考虑迁移 Milvus
- [API 不稳定] → 3 次重试 + 本地缓存高频查询
