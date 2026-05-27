## ADDED Requirements

### Requirement: One-click knowledge base initialization
The system SHALL provide a sidebar button "初始化规范库" that parses all PDFs, chunks them, embeds with BGE-M3, and persists to ChromaDB.

### Requirement: Idempotent build
The system SHALL skip already-imported documents by content hash to avoid duplication on re-initialization.

### Requirement: Stats display
The system SHALL display knowledge base statistics: number of standards loaded and total clause count in the sidebar.
