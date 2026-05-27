## ADDED Requirements

### Requirement: Citation-formatted answers
The system SHALL generate answers with precise citations in format: "根据《规范名》GB XXXX-20XX 第X.X.X条：原文内容"

### Requirement: Honest fallback on no results
The system SHALL clearly state when no relevant clauses are found, suggesting alternative keywords or specific standard names.

#### Scenario: Retrieval returns no results
- **WHEN** search returns empty results
- **THEN** the system responds with "当前规范库未收录与您问题相关的内容" and suggests alternatives

### Requirement: Anti-hallucination guard
The system SHALL only cite clause numbers that appear in retrieved documents, never fabricating clause numbers.
