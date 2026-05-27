# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目结构

```
E:\pycharm_project2\
├── tiktok_project/          # AI 评论分析 Agent
├── Code_LA\yuan_gui_tong\   # 园规通 — 风景园林设计规范 RAG 助手
└── openspec/                # OpenSpec 变更管理
    ├── changes/
    │   ├── tiktok-agent-comment-analysis/      # 评论分析 Agent 提案
    │   └── yuan-gui-tong-design-standards-rag/ # 园规通 RAG 提案
    ├── specs/                # 已归档的能力规格
    └── archive/              # 已归档的变更
```

## 子项目快速入口

| 项目 | 启动命令 | 端口 | 文档 |
|------|---------|------|------|
| AI 评论分析 Agent | `cd tiktok_project && ..\.venv\Scripts\streamlit run app.py` | 8502 | tiktok_project/CLAUDE.md |
| 园规通 RAG | `cd Code_LA\yuan_gui_tong && .venv\Scripts\streamlit run app.py` | 8503 | Code_LA/yuan_gui_tong/CLAUDE.md |

## 共享约定

- 所有项目文件不放 C 盘（除非别无选择）
- LLM 全用 DeepSeek API (`deepseek-chat`)，Key 在各自 `.env` 文件中
- 对话使用中文
- 使用 OpenSpec 管理规范化提案流程（`/opsx:propose` → `/opsx:apply` → `/opsx:archive`）
