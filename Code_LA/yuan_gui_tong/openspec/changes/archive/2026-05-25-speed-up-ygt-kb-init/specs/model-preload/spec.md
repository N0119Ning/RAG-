## ADDED Requirements

### Requirement: Model cache check on startup
The system SHALL check if BGE-M3 model is cached locally on Streamlit startup. If not, display a pre-download button in the sidebar instead of letting the user discover the 2GB download during initialization.

#### Scenario: First run without model
- **WHEN** the app starts and BGE-M3 is not cached
- **THEN** sidebar shows "BGE-M3 模型未下载" with a "预下载模型 (~2GB)" button

### Requirement: Pre-download progress
The system SHALL show download progress when pre-downloading BGE-M3 model.

#### Scenario: User clicks pre-download
- **WHEN** user clicks "预下载模型" button
- **THEN** a progress bar shows download status, and after completion the KB init button becomes available
