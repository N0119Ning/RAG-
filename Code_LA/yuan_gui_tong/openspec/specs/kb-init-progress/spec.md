# kb-init-progress Specification

## Purpose
TBD - created by archiving change speed-up-ygt-kb-init. Update Purpose after archive.
## Requirements
### Requirement: Step-by-step progress display
The system SHALL display initialization progress in 4 distinct steps: parsing PDFs, chunking clauses, embedding, and importing to ChromaDB.

#### Scenario: Normal initialization
- **WHEN** user clicks "初始化规范库"
- **THEN** the UI shows "步骤 1/4: 解析 PDF... (3/8)", "步骤 2/4: 切分条款... (45 条)", "步骤 3/4: 向量化...", "步骤 4/4: 导入 ChromaDB..."

### Requirement: Per-file PDF parsing progress
The system SHALL report which PDF is currently being parsed and which page (for long documents).

#### Scenario: Parsing 8 PDFs
- **WHEN** parsing the 3rd PDF
- **THEN** the UI shows "正在解析 GB50420-2007 (3/8)..."

### Requirement: Skip OCR-requiring PDFs during init
The system SHALL flag PDFs with low Chinese text (< 80 chars/page average) as `needs_ocr: true` and skip full OCR during initialization, showing a count of skipped files afterward.

#### Scenario: Low-text PDF detected
- **WHEN** GB50180-2018 is found to have only 645 Chinese chars across 43 pages
- **THEN** the system skips full OCR, marks it, and shows "4 份规范文本较少，可在初始化后单独进行 OCR 增强"

