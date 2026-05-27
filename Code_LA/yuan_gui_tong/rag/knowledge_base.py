"""Knowledge base: orchestrates PDF parsing → clause chunking → embedding → storage."""

import os
from pathlib import Path
from typing import List, Optional
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .embedder import EmbeddingManager  # torch must load before paddle
from .retriever import HybridRetriever
from .pdf_parser import PDFParser, ParsedDocument
from .clause_chunker import ClauseChunker


class KnowledgeBase:
    def __init__(
        self,
        collection_name: str = "ygt_design_standards",
        persist_directory: str = "./data/chroma_db",
        pdf_dir: str = "./data/standards",
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.pdf_dir = pdf_dir

        os.makedirs(persist_directory, exist_ok=True)

        self.embedder = EmbeddingManager()
        self.retriever = HybridRetriever(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedder=self.embedder,
        )
        self.parser = PDFParser(pdf_dir=pdf_dir)
        self.chunker = ClauseChunker()
        self.low_text_pdfs = []  # PDFs that may need OCR enhancement

    @property
    def collection(self):
        return self.retriever.collection

    def build(self, pdf_dir: Optional[str] = None, progress_callback=None):
        if pdf_dir:
            self.pdf_dir = pdf_dir
            self.parser = PDFParser(pdf_dir=pdf_dir)

        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"[KnowledgeBase] 集合已存在 {existing_count} 条记录，跳过构建")
            if progress_callback:
                progress_callback("done", "知识库已存在，无需重新构建", existing_count, existing_count)
            return

        # Step 1: Parse PDFs
        if progress_callback:
            progress_callback("step", "正在解析PDF", 0, 0)

        docs = self.parser.parse_all(
            progress_callback=progress_callback
        )
        if not docs:
            print("[KnowledgeBase] 未找到 PDF 文件")
            return

        # Collect low-text PDFs for OCR hint
        self.low_text_pdfs = [f"{d.standard_code} {d.standard_name}"
                         for d in docs if d.needs_ocr]

        # Step 2: Chunk clauses
        if progress_callback:
            progress_callback("step", "正在切分条款", 0, len(docs))

        all_clauses = self.chunker.chunk_all(docs)
        total_clauses = len(all_clauses)

        if progress_callback:
            progress_callback("step", f"正在向量化 ({total_clauses} 条)", 0, total_clauses)

        # Step 3: Build id/text/metadata lists
        ids, texts, metadatas = [], [], []
        for i, clause in enumerate(all_clauses):
            ids.append(f"clause_{i:05d}")
            texts.append(clause.page_content)
            metadatas.append(clause.metadata)

        # Step 4: Import to ChromaDB
        if progress_callback:
            progress_callback("step", f"正在导入向量库 ({len(texts)} 条)", 0, len(texts))

        # Batch upsert in chunks of 500
        batch_size = 500
        for start in range(0, len(texts), batch_size):
            end = min(start + batch_size, len(texts))
            self.collection.upsert(
                ids=ids[start:end],
                documents=texts[start:end],
                metadatas=metadatas[start:end],
            )
            if progress_callback:
                progress_callback("step", f"正在导入向量库 ({len(texts)} 条)", end, len(texts))

        if progress_callback:
            progress_callback("done", "知识库构建完成", total_clauses, total_clauses)

        print(f"[KnowledgeBase] 构建完成：{total_clauses} 条条款已入库")

        if self.low_text_pdfs:
            print(f"[KnowledgeBase] 注意：以下规范文本较少，建议 OCR 增强: {', '.join(self.low_text_pdfs)}")

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        return self.retriever.retrieve(query, top_k=top_k)

    def get_stats(self) -> dict:
        all_data = self.collection.get(include=["metadatas"])
        metadatas = all_data.get("metadatas", [])

        total = len(metadatas)
        mandatory_count = sum(1 for m in metadatas if m.get("is_mandatory"))

        standards = defaultdict(int)
        for m in metadatas:
            code = m.get("standard_code", "未知")
            standards[code] += 1

        return {
            "total_clauses": total,
            "mandatory_count": mandatory_count,
            "standards": dict(sorted(standards.items())),
        }

    def clear(self):
        try:
            self.retriever._client.delete_collection(name=self.collection_name)
        except ValueError:
            pass
        self.retriever.collection = self.retriever._client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedder.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"[KnowledgeBase] 已清空集合: {self.collection_name}")
