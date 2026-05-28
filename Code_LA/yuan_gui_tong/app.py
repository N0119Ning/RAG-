import torch  # Must preload before any other imports to resolve DLL deps

import streamlit as st
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="园规通 — 风景园林设计规范智能助手",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #166534;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .ref-block {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
    .ref-block .ref-header {
        font-weight: bold;
        color: #166534;
        margin-bottom: 4px;
    }
    .ref-block .ref-body {
        color: #374151;
    }
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .progress-log {
        font-size: 0.85rem;
        color: #64748b;
        max-height: 200px;
        overflow-y: auto;
        background: #f1f5f9;
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


def check_model_cache() -> bool:
    """Check if BGE-M3 model is cached locally."""
    model_path = project_root / "models" / "BAAI" / "bge-m3"
    required_files = [
        "config.json",
        "pytorch_model.bin",
        "sentencepiece.bpe.model",
        "tokenizer.json",
        "special_tokens_map.json",
    ]
    if not model_path.exists():
        return False
    return all((model_path / f).exists() for f in required_files)


def init_session():
    defaults = {
        "messages": [],
        "kb": None,
        "kb_ready": False,
        "api_key_set": False,
        "model_cached": check_model_cache(),
        "model_downloading": False,
        "kb_building": False,
        "progress_log": [],
        "low_text_pdfs": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_ref_block(meta: dict, content: str):
    code = meta.get("standard_code", "未知")
    name = meta.get("standard_name", "")
    clause = meta.get("clause_number", "")
    clause_str = f" 第{clause}条" if clause else ""
    header = f"{code} {name}{clause_str}"
    preview = content[:300] + ("..." if len(content) > 300 else "")
    st.markdown(f"""
    <div class="ref-block">
        <div class="ref-header">{header}</div>
        <div class="ref-body">{preview}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    init_session()

    st.markdown('<div class="main-title">园规通</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">风景园林设计规范智能助手 — 自然语言查询，精确条款引用</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### 配置")

        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            value=os.environ.get("DEEPSEEK_API_KEY", ""),
            placeholder="sk-...",
            help="用于调用 DeepSeek 大模型生成回答",
        )
        if api_key and api_key != os.environ.get("DEEPSEEK_API_KEY", ""):
            os.environ["DEEPSEEK_API_KEY"] = api_key
            st.session_state.api_key_set = True

        st.markdown("---")

        # ---- Model pre-check ----
        if not st.session_state.model_cached:
            st.warning("BGE-M3 模型未下载 (~2GB)")
            if st.button("预下载模型", use_container_width=True):
                st.session_state.model_downloading = True

        if st.session_state.model_downloading:
            with st.spinner("正在下载 BGE-M3 模型，约需数分钟..."):
                try:
                    from rag.embedder import EmbeddingManager
                    EmbeddingManager()
                    st.session_state.model_cached = True
                    st.session_state.model_downloading = False
                    st.success("模型下载完成！")
                    st.rerun()
                except Exception as e:
                    st.error(f"下载失败: {e}")
                    st.session_state.model_downloading = False

        # ---- Knowledge Base ----
        st.markdown("### 知识库")

        if not st.session_state.model_cached:
            st.info("请先下载 BGE-M3 模型后再初始化知识库")
        else:
            col1, col2 = st.columns(2)

            with col1:
                init_disabled = st.session_state.kb_building
                if st.button("初始化知识库", type="primary", use_container_width=True,
                             disabled=init_disabled):
                    if not st.session_state.api_key_set and not os.environ.get("DEEPSEEK_API_KEY"):
                        st.error("请先设置 API Key")
                    else:
                        st.session_state.kb_building = True
                        st.session_state.progress_log = []

            with col2:
                if st.button("加载已有库", use_container_width=True,
                             disabled=st.session_state.kb_building):
                    try:
                        from rag.knowledge_base import KnowledgeBase
                        kb = KnowledgeBase()
                        stats = kb.get_stats()
                        st.session_state.kb = kb
                        st.session_state.kb_ready = True
                        st.success(f"已加载，{stats['total_clauses']} 条条款")
                    except Exception as e:
                        st.error(f"加载失败: {e}")

        # ---- Build progress display ----
        if st.session_state.kb_building:
            progress_bar = st.progress(0)
            progress_status = st.empty()
            progress_detail = st.empty()

            try:
                from rag.knowledge_base import KnowledgeBase

                # Step tracking
                step_map = {"parse": 0, "chunk": 0, "embed": 0, "import": 0, "done": 0}

                def on_progress(step, detail, current, total):
                    step_labels = {
                        "parse": "解析 PDF",
                        "chunk": "切分条款",
                        "embed": "向量化",
                        "import": "导入向量库",
                        "done": "完成",
                    }
                    label = step_labels.get(step, step)
                    if total and total > 0:
                        pct = min(current / total, 1.0)
                        progress_bar.progress(pct)
                        progress_status.text(f"步骤: {label}")
                        progress_detail.text(f"{detail} ({current}/{total})")
                    else:
                        progress_status.text(f"步骤: {label}")
                        progress_detail.text(detail)

                    entry = f"[{label}] {detail}"
                    if entry not in st.session_state.progress_log:
                        st.session_state.progress_log.append(entry)

                kb = KnowledgeBase()
                kb.build(progress_callback=on_progress)
                st.session_state.kb = kb
                st.session_state.kb_ready = True
                st.session_state.low_text_pdfs = getattr(kb, 'low_text_pdfs', [])
                st.session_state.kb_building = False

                stats = kb.get_stats()
                progress_bar.progress(1.0)
                progress_status.empty()
                progress_detail.empty()
                st.success(f"构建完成！共 {stats['total_clauses']} 条条款")

                if st.session_state.low_text_pdfs:
                    st.info(f"{len(st.session_state.low_text_pdfs)} 份规范文本较少，可在下方进行 OCR 增强")

            except Exception as e:
                st.session_state.kb_building = False
                st.error(f"构建失败: {e}")
                st.session_state.progress_log.append(f"[错误] {e}")

            # Show progress log in expandable section
            if st.session_state.progress_log:
                with st.expander("查看构建日志"):
                    for entry in st.session_state.progress_log:
                        st.text(entry)

        # ---- KB status & OCR enhancement ----
        if st.session_state.kb_ready and st.session_state.kb:
            try:
                stats = st.session_state.kb.get_stats()
                st.markdown(f"**状态：** 就绪 | {stats['total_clauses']} 条条款 | {stats['mandatory_count']} 条强制")
                with st.expander("查看规范分布"):
                    for code, count in stats.get("standards", {}).items():
                        st.text(f"  {code}: {count} 条")

                # OCR enhancement for low-text PDFs
                if st.session_state.low_text_pdfs:
                    st.markdown("---")
                    st.markdown("### OCR 增强处理")
                    st.info(f"{len(st.session_state.low_text_pdfs)} 份规范文本较少: "
                            f"{', '.join(st.session_state.low_text_pdfs[:3])}"
                            f"{'...' if len(st.session_state.low_text_pdfs) > 3 else ''}")
                    if st.button("OCR 增强处理", use_container_width=True):
                        with st.spinner("正在进行 OCR 增强处理，可能需要较长时间..."):
                            try:
                                from rag.pdf_parser import PDFParser
                                from rag.clause_chunker import ClauseChunker

                                parser = PDFParser(pdf_dir="data/standards")
                                docs = parser.parse_all()
                                # re-chunk only the OCR-enhanced docs
                                chunker = ClauseChunker()
                                clauses = chunker.chunk_all(docs)

                                # Rebuild collection
                                st.session_state.kb.clear()
                                ids, texts, metadatas = [], [], []
                                for i, c in enumerate(clauses):
                                    ids.append(f"clause_{i:05d}")
                                    texts.append(c.page_content)
                                    metadatas.append(c.metadata)

                                CHROMA_BATCH = 32
                                for start in range(0, len(texts), CHROMA_BATCH):
                                    end = min(start + CHROMA_BATCH, len(texts))
                                    st.session_state.kb.collection.upsert(
                                        ids=ids[start:end],
                                        documents=texts[start:end],
                                        metadatas=metadatas[start:end],
                                    )

                                st.session_state.low_text_pdfs = []
                                new_stats = st.session_state.kb.get_stats()
                                st.success(f"OCR 增强完成！共 {new_stats['total_clauses']} 条条款")
                                st.rerun()
                            except Exception as e:
                                st.error(f"OCR 增强失败: {e}")
            except Exception:
                pass

        st.markdown("---")
        st.info("""
        **使用步骤：**
        1. 输入 DeepSeek API Key
        2. 预下载 BGE-M3 模型（首次使用）
        3. 点击「初始化知识库」
        4. 在对话框中输入问题
        """)

    # ---- Main chat area ----
    if not st.session_state.kb_ready:
        st.markdown("""
        ### 欢迎使用园规通！

        本工具覆盖以下设计规范：
        - **GB 50180** 城市居住区规划设计标准
        - **GB 50016** 建筑设计防火规范
        - **GB 50420** 城市绿地设计规范
        - **CJJ 82** 园林绿化工程施工及验收规范
        - 及其他风景园林相关国标/行标

        **开始使用：** 在左侧边栏配置 API Key 并初始化知识库。
        """)
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and "results" in msg:
                st.markdown(msg["content"])
                with st.expander("查看引用来源"):
                    for r in msg["results"]:
                        render_ref_block(r.get("metadata", {}), r.get("content", ""))
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("输入规范查询问题，如：居住区绿地率最低要求是多少？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在检索..."):
                try:
                    results = st.session_state.kb.search(prompt, top_k=5)

                    if not os.environ.get("DEEPSEEK_API_KEY"):
                        answer = "请先在侧边栏设置 DeepSeek API Key。"
                        st.markdown(answer)
                        st.markdown("### 检索结果（无 LLM 回答）")
                        for r in results:
                            render_ref_block(r.get("metadata", {}), r.get("content", ""))
                    else:
                        from utils.llm_client import LLMClient
                        from utils.answer_generator import AnswerGenerator

                        llm = LLMClient()
                        gen = AnswerGenerator(llm)
                        answer = gen.generate(prompt, results)
                        answer = answer.replace("~", "～")
                        st.markdown(answer)

                        if results:
                            with st.expander(f"查看 {len(results)} 条引用来源"):
                                for r in results:
                                    render_ref_block(r.get("metadata", {}), r.get("content", ""))

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "results": results,
                    })

                except Exception as e:
                    error_msg = f"查询失败: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "results": [],
                    })

    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()