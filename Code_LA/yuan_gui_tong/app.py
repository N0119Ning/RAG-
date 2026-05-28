import torch  # Must preload before any other imports to resolve DLL deps

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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
        font-size: 1.6rem;
        font-weight: bold;
        color: #166534;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 1rem;
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
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .chat-link {
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .chat-link:hover {
        background: #e2e8f0;
    }
    .kb-status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 4px;
    }
    .kb-status-dot.ready { background: #22c55e; }
    .kb-status-dot.busy { background: #f59e0b; }
    .welcome-overlay {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 16px;
        padding: 32px 40px;
        text-align: center;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

FULL_NAMES = {
    "CJJ37": "城市道路绿化设计标准",
    "CJJ82": "园林绿化工程施工及验收规范",
    "CJJT91": "风景园林基本术语标准",
    "GB50016": "建筑设计防火规范",
    "GB50180": "城市居住区规划设计标准",
    "GB50420": "城市绿地设计规范",
    "GB50763": "无障碍设计规范",
    "GB51192": "公园设计规范",
    "GB55014": "园林绿化工程项目规范",
}


def init_session():
    defaults = {
        "messages": [],
        "kb": None,
        "kb_ready": False,
        "kb_building": False,
        "progress_log": [],
        "welcome_dismissed": False,
        "highlight_msg": -1,
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
        '<div class="sub-title">风景园林设计规范智能助手 · 9本规范 · 1168条条款</div>',
        unsafe_allow_html=True,
    )

    # ---- Welcome overlay ----
    if not st.session_state.welcome_dismissed:
        with st.container():
            st.markdown("""
            <div class="welcome-overlay">
                <h2>欢迎使用园规通！</h2>
                <p style="color:#374151;font-size:1rem;">
                覆盖 <b>9本</b> 风景园林核心国标/行标<br>
                <b>1168条</b> 条款 · PaddleOCR 扫描件精准识别<br>
                BGE-M3 语义检索 + DeepSeek 精确引用回答
                </p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("开始使用", type="primary", use_container_width=True):
                    st.session_state.welcome_dismissed = True
                    st.rerun()
            return

    # ---- Sidebar ----
    with st.sidebar:
        # Conversation history
        st.markdown("### 对话记录")
        if not st.session_state.messages:
            st.caption("暂无对话")
        else:
            user_msgs = [(i, m) for i, m in enumerate(st.session_state.messages)
                         if m["role"] == "user"]
            for idx, msg in user_msgs[-20:]:
                label = msg["content"][:40] + ("..." if len(msg["content"]) > 40 else "")
                btn_label = f"#{idx//2 + 1} {label}"
                if st.button(btn_label, key=f"hist_{idx}", use_container_width=True):
                    st.session_state.highlight_msg = idx
                    st.rerun()

        st.markdown("---")

        # KB controls
        st.markdown("### 知识库")

        if st.session_state.kb_ready and st.session_state.kb:
            stats = st.session_state.kb.get_stats()
            st.markdown(
                f'<span class="kb-status-dot ready"></span> '
                f'<b>就绪</b> · {stats["total_clauses"]} 条条款 · '
                f'{stats["mandatory_count"]} 条强制',
                unsafe_allow_html=True,
            )

            with st.expander("已加载规范"):
                for code, count in sorted(stats.get("standards", {}).items()):
                    name = FULL_NAMES.get(code, "")
                    st.text(f"{code} {name}  {count}条")
        else:
            st.markdown(
                '<span class="kb-status-dot busy"></span> <b>未加载</b>',
                unsafe_allow_html=True,
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("初始化", type="primary", use_container_width=True,
                         disabled=st.session_state.kb_building):
                load_and_build_kb()
        with col2:
            if st.button("加载已有", use_container_width=True,
                         disabled=st.session_state.kb_building):
                load_existing_kb()

        # Build progress — show in main area for visibility
        if st.session_state.kb_building:
            st.markdown("---")
            with st.status("正在初始化知识库...", expanded=True) as build_status:
                st.write("此过程包含 PDF 解析、条款切分、向量化，首次约需 10-20 分钟")
                st.write("进度将在完成后显示")
            # Note: real-time progress not possible due to Streamlit single-thread;
            # the build runs in load_and_build_kb() and shows result on completion.

        st.markdown("---")
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # ---- Main chat area ----
    if st.session_state.kb_building:
        with st.spinner(""):
            st.markdown("### 🔧 正在初始化知识库...")
            st.caption("首次构建包含 PDF 解析、OCR 识别、条款切分、向量化")
            st.caption("请耐心等待，完成后将自动显示聊天界面")
        return

    if not st.session_state.kb_ready:
        st.info("在侧边栏点击「加载已有」加载知识库，或「初始化」构建新库。")
        return

    for idx, msg in enumerate(st.session_state.messages):
        # Highlight marker
        if idx == st.session_state.highlight_msg:
            st.markdown(
                '<div style="background:#dcfce7;color:#166534;padding:4px 12px;'
                'border-radius:6px;font-size:0.85rem;font-weight:bold;text-align:center;">'
                '▼ 定位到对话 #' + str(idx // 2 + 1) + '</div>',
                unsafe_allow_html=True,
            )
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and "results" in msg:
                st.markdown(msg["content"])
                n_results = len(msg["results"])
                with st.expander(f"查看 {n_results} 条引用来源"):
                    st.caption(f"检索到 {n_results} 条相关条款，按相似度排序")
                    for i, r in enumerate(msg["results"], 1):
                        sim = r.get("similarity", 0)
                        st.caption(f"#{i} 相似度: {sim:.2%}")
                        render_ref_block(r.get("metadata", {}), r.get("content", ""))
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("输入规范查询问题，如：居住区绿地率最低要求是多少？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status = st.status("处理中...", expanded=False)
            try:
                status.update(label="正在检索...", state="running")
                results = st.session_state.kb.search(prompt, top_k=5)

                status.update(label="正在生成回答...", state="running")
                from utils.llm_client import LLMClient
                from utils.answer_generator import AnswerGenerator

                llm = LLMClient()
                gen = AnswerGenerator(llm)
                answer = gen.generate(prompt, results)
                answer = answer.replace("~", "～")
                status.update(label="完成", state="complete")

                st.markdown(answer)

                if results:
                    with st.expander(f"查看 {len(results)} 条引用来源"):
                        for r in results:
                            render_ref_block(r.get("metadata", {}), r.get("content", ""))

                with st.expander("报告此回答有问题"):
                    issue = st.selectbox(
                        "问题类型",
                        ["", "条款号编造/错误", "引用了错误的规范",
                         "答案不完整/遗漏", "OCR乱码导致答非所问",
                         "无结果/检索不到", "其他"],
                        key=f"issue_{len(st.session_state.messages)}",
                    )
                    if st.button("提交报告", key=f"submit_{len(st.session_state.messages)}"):
                        if issue:
                            from utils.badcase_logger import log_badcase
                            log_badcase(prompt, answer, results, issue)
                            st.success("已记录，谢谢反馈！")
                        else:
                            st.warning("请选择问题类型")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "results": results,
                })

            except Exception as e:
                status.update(label=f"失败", state="error")
                error_msg = f"查询失败: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "results": [],
                })


def load_and_build_kb():
    st.session_state.kb_building = True
    st.session_state.progress_log = []

    try:
        from rag.knowledge_base import KnowledgeBase

        def on_progress(step, detail, current, total):
            label = {"parse": "解析", "embed": "嵌入", "done": "完成"}.get(step, step)
            entry = f"[{label}] {detail}"
            if entry not in st.session_state.progress_log:
                st.session_state.progress_log.append(entry)

        kb = KnowledgeBase()
        kb.build(progress_callback=on_progress)
        st.session_state.kb = kb
        st.session_state.kb_ready = True
        st.session_state.kb_building = False
        st.session_state.progress_log.append("[完成] 构建完毕")
        st.rerun()
    except Exception as e:
        st.session_state.kb_building = False
        st.session_state.progress_log.append(f"[错误] {e}")
        st.error(f"构建失败: {e}")


def load_existing_kb():
    with st.spinner("正在加载 BGE-M3 模型 (~2GB)...约需 30 秒"):
        try:
            from rag.knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            stats = kb.get_stats()
            if stats["total_clauses"] == 0:
                st.warning("知识库为空，请先点击「初始化」构建")
            else:
                st.session_state.kb = kb
                st.session_state.kb_ready = True
                st.success(f"已加载 {stats['total_clauses']} 条条款 · "
                          f"{len(stats['standards'])} 本规范 · BGE-M3 就绪")
        except Exception as e:
            st.error(f"加载失败: {e}")


if __name__ == "__main__":
    main()
