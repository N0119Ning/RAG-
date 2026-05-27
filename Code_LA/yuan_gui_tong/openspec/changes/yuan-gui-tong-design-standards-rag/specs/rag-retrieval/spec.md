## ADDED Requirements

### Requirement: BGE-M3 Chinese-optimized embedding
The system SHALL use BAAI/bge-m3 (1024-dimensional) for embedding with normalized vectors.

### Requirement: Hybrid search with jieba keywords
The system SHALL combine vector similarity (50%) and jieba keyword matching (50%) for retrieval ranking.

#### Scenario: Keyword-heavy query
- **WHEN** user asks "小区主路宽度要求"
- **THEN** jieba extracts ["小区", "主路", "宽度"] for keyword matching alongside vector search

### Requirement: Top-k retrieval with metadata
The system SHALL return top-5 results with standard_code, standard_name, clause_number, and page_range metadata.
