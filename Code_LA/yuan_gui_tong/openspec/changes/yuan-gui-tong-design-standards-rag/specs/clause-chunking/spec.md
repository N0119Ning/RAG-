## ADDED Requirements

### Requirement: Markdown heading hierarchy
The system SHALL parse MinerU Markdown output using heading levels (## 章 → ### 节 → #### 条) to establish clause structure before applying regex.

### Requirement: Clause number pattern matching
The system SHALL detect clause numbers using regex patterns: decimal numbering (3.1.2), Chinese format (第3.1.2条), and Roman numeral format (III-1.2).

### Requirement: Mandatory clause detection
The system SHALL detect mandatory clauses by scanning for keywords: 必须, 严禁, 应, 不应.

### Requirement: Fallback to heading-based chunking
The system SHALL fall back to heading-based chunking when no clause numbers are detected in a section.

### Requirement: Long clause splitting
The system SHALL split clauses exceeding 3000 characters by paragraph boundaries (double newlines).
