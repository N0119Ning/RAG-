## 1. PDF 解析管道 (MinerU)

- [x] 1.1 MinerU CLI 调用（magic-pdf 解析 PDF → Markdown）
- [x] 1.2 文件名解析（规范编号 + 规范名称）
- [x] 1.3 Markdown 文本清洗（去页眉页脚、合并断行）

## 2. 条款切分

- [x] 2.1 Markdown 标题层级解析（## 章 → ### 节 → 条款段落）
- [x] 2.2 条款号正则匹配（3.1.2 / 第3.1.2条 / III-1.2）
- [x] 2.3 强条检测（必须/严禁/应/不应）
- [x] 2.4 长条款二次切分 + 短条款合并

## 3. RAG 检索引擎

- [x] 3.1 BGE-M3 embedding（1024维，中文优化）
- [x] 3.2 ChromaDB 持久化 + 余弦相似度
- [x] 3.3 jieba 中文分词关键词提取
- [x] 3.4 混合检索（向量 50% + 关键词 50%）

## 4. 回答生成

- [x] 4.1 DeepSeek-chat API 封装 + 3 次重试
- [x] 4.2 引用格式 prompt（规范名 + 条款号 + 原文）
- [x] 4.3 无结果诚实反馈 + 反幻觉 guard

## 5. Streamlit 前端

- [x] 5.1 问答界面（chat_input + chat_message）
- [x] 5.2 侧边栏（API Key 配置 + 初始化按钮 + 知识库状态）
- [x] 5.3 引用块 CSS 渲染（规范名 + 条款号 + 来源标注）
- [x] 5.4 欢迎页 + 空状态提示

## 6. 文档

- [x] 6.1 YUAN_GUI_TONG_DESIGN.md — 产品设计说明
