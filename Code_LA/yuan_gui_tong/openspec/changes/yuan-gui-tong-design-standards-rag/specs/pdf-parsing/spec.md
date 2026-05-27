## ADDED Requirements

### Requirement: MinerU PDF to Markdown conversion
The system SHALL convert PDF standards to Markdown using MinerU (magic-pdf CLI), producing clean structured text with preserved headings, paragraphs, and tables.

#### Scenario: Multi-column Chinese PDF
- **WHEN** a multi-column design standard PDF is processed
- **THEN** MinerU outputs correctly ordered Markdown with reading order preserved

#### Scenario: Scanned/image PDF
- **WHEN** a PDF lacks text layer (scanned document)
- **THEN** MinerU's built-in OCR recovers text without external fallback

### Requirement: Markdown text cleaning
The system SHALL clean MinerU output by removing residual headers/footers, normalizing whitespace, and merging broken lines within paragraphs.

#### Scenario: Clean typical MinerU output
- **WHEN** MinerU produces Markdown with page numbers and repeated headers
- **THEN** page artifacts are removed and paragraph text is continuous

### Requirement: Filename metadata parsing
The system SHALL parse standard code and name from filename pattern `GB50180-2018_城市居住区规划设计标准.pdf`.
