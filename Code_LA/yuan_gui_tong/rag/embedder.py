"""BGE-M3 embedding manager with ChromaDB integration."""

import os
from pathlib import Path
from chromadb.api.types import EmbeddingFunction
from sentence_transformers import SentenceTransformer

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

_LOCAL_MODEL = Path(__file__).parent.parent / "models" / "BAAI" / "bge-m3"


class BgeM3EmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self._model_name = str(_LOCAL_MODEL) if _LOCAL_MODEL.exists() else model_name
        self._model = None

    @property
    def _lazy_model(self):
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def __call__(self, texts):
        return self._lazy_model.encode(
            list(texts), batch_size=8, show_progress_bar=False
        ).tolist()


class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        self.provider = "BGE-M3"
        self.embedding_function = BgeM3EmbeddingFunction(model_name)

    def embed_query(self, text: str):
        return self.embedding_function([text])[0]

    def embed_documents(self, texts: list):
        return self.embedding_function(texts)

    def get_dimension(self) -> int:
        return 1024
