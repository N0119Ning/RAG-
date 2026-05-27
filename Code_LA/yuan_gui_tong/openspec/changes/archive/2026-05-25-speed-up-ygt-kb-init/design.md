## Context

当前知识库初始化的 `KnowledgeBase.build()` 没有对外暴露进度回调。Streamlit 只能看到 `st.spinner` 包围的整段代码，内部每步耗时完全黑盒。

## Goals / Non-Goals

**Goals:**
- 初始化过程中显示 4 步进度：解析 PDF → 切分条款 → 向量化 → 入库
- 每步显示 : "正在解析 GB50180-2018 (3/8)..."
- 首次运行前检查 BGE-M3 是否已缓存，未缓存则提示用户
- 缺字 PDF（需要 OCR 的）先跳过，初始化完成后单独提示

**Non-Goals:**
- 不更换 BGE-M3 模型（保持检索质量）
- 不改变 ChromaDB 存储结构
- 不优化单个 PDF 解析速度

## Decisions

| 决策 | 选型 | 理由 |
|------|------|------|
| 进度机制 | `build()` 方法接受 `progress_callback` | 非侵入式，调用方可自定义 UI |
| 回调格式 | `(step, detail, current, total)` | 统一接口，Streamlit / CLI 通用 |
| 模型预检 | `app.py` 启动时异步检查 BGE-M3 缓存 | 不阻塞 UI 渲染 |
| OCR 跳过 | 中文字数 < 80 的 PDF 标记为 `needs_ocr: true` | 不丢数据，初始化后可见 |

## Risks / Trade-offs

- [跳过 OCR 可能丢失内容] → 初始化后侧边栏显示 "X 份规范需 OCR 处理"，可手动触发
- [进度回调增加复杂度] → 仅在 `build()` 新增可选参数，不影响无回调场景
