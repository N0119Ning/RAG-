## 1. 进度回调机制

- [x] 1.1 `knowledge_base.py` 的 `build()` 方法新增 `progress_callback` 可选参数
- [x] 1.2 `progress_callback(step, detail, current, total)` — step: 'parse'|'chunk'|'embed'|'import'
- [x] 1.3 `pdf_parser.py` 的 `parse_all()` 暴露当前 PDF 索引和总数

## 2. Streamlit 分步进度 UI

- [x] 2.1 替换单一 `st.spinner` 为 `st.progress` + 分步 `st.write`
- [x] 2.2 显示格式: "步骤 X/4: <描述>... (N/M)"
- [x] 2.3 初始化完成后保留进度日志在可折叠区域

## 3. OCR 跳过

- [x] 3.1 `pdf_parser.py` 新增 `skip_ocr=True` 参数，跳过低文本页的 OCR
- [x] 3.2 收集低文本 PDF 列表，初始化完成后 `st.info` 提示
- [x] 3.3 侧边栏新增 "OCR 增强处理" 按钮（触发对已标记 PDF 的 OCR 重处理）

## 4. 模型预检

- [x] 4.1 `app.py` 启动时检查 BGE-M3 缓存状态
- [x] 4.2 未缓存时侧边栏显示 "预下载模型" 按钮
- [x] 4.3 下载进度用 `st.progress` 展示
