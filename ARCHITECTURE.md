# IRMS Architecture Documentation

## System Overview

The Intelligent Release Management Scanner (IRMS) implements a sophisticated pipeline for automated code analysis, modification, and release management. This document explains how the implementation maps to the architecture diagram.

## Architecture Mapping

### 1. Input Sources
**Diagram Component**: Input Sources (Code Repositories, CI/CD Pipelines)
**Implementation**: `modules/ingestion.py`

- **FileIngestion class**
  - Reads Python source files from `inputs/code/`
  - Parses PDF and text documents from `inputs/docs/`
  - Creates Abstract Syntax Trees (AST) for code analysis
  - Maintains file inventory and metadata

**Key Methods**:
- `ingest_python_files()` - Loads and parses .py files
- `ingest_documents()` - Extracts text from PDFs and docs
- `get_summary()` - Provides ingestion statistics

### 2. Ingestion & Parsing
**Diagram Component**: Ingestion & Parsing (Code & Doc Parsing, Dependency Analysis)
**Implementation**: `utils/ast_helper.py`, `utils/pdf_parser.py`

**AST Helper** (`ast_helper.py`):
- Parses Python source into AST nodes
- Extracts function and class metadata
- Identifies imports and dependencies
- Counts lines of code (total, code, comments, blanks)

**PDF Parser** (`pdf_parser.py`):
- Extracts text from PDF documents
- Handles text file reading
- Provides context from supporting documentation

**Key Functions**:
- `parse_python_file()` - Creates AST from source
- `get_function_info()` - Extracts function metadata
- `get_class_info()` - Analyzes class structures
- `extract_text_from_pdf()` - Reads PDF content

### 3. Security & Change Analysis
**Diagram Component**: Security & Change Analysis (SAST Scan, Vuln & Secrets Scan, Change Detection)
**Implementation**: `modules/code_analyzer.py`, `modules/change_detector.py`

**Code Analyzer** (`code_analyzer.py`):
- Performs static application security testing (SAST)
- Calculates cyclomatic complexity using Radon
- Computes maintainability index
- Detects code issues and anti-patterns
- Identifies security concerns (bare excepts, print statements, missing docstrings)

**Change Detector** (`change_detector.py`):
- Generates unified diffs between versions
- Calculates change statistics (additions, deletions, modifications)
- Provides visualizations of changes
- Tracks modification impact

**Key Analyses**:
- Complexity scoring (A-F ranks)
- Issue detection (severity-based)
- Line-by-line change tracking
- Diff generation for reporting

### 4. Product Intelligence Model
**Diagram Component**: Product Intelligence Model (Components Map, Data Flows & Risks, Incremental Learning)
**Implementation**: `modules/ai_engine.py`

**AI Engine** (`ai_engine.py`):
- Integrates Google Gemini 1.5 Flash API for intelligent analysis
- Builds comprehensive prompts with context
- Applies modifications based on natural language queries
- Generates explanations for all changes
- Learns from static analysis results and documentation

**Intelligence Features**:
- Context-aware code understanding
- Natural language query processing
- Best practices enforcement
- Explanation generation
- Impact prediction

**Key Methods**:
- `analyze_and_modify()` - Main AI analysis pipeline
- `_build_analysis_prompt()` - Context assembly
- `_parse_ai_response()` - Extract code and explanations
- `get_impact_summary()` - Calculate change impact

### 5. Release Analysis & Reporting
**Diagram Component**: Release Analysis & Reporting (Impact Assessment, Risk Prioritization, Test Recommendations)
**Implementation**: `modules/risk_assessor.py`

**Risk Assessor** (`risk_assessor.py`):
- Multi-factor risk scoring algorithm
- Weighted risk components:
  - Complexity Risk (30%)
  - Change Volume Risk (20%)
  - Critical Function Risk (30%)
  - Issue Severity Risk (20%)
- Gate decision logic (PASS/WARN/BLOCK)
- Recommendation generation

**Risk Gates**:
- **PASS** (< 30): Low risk, standard review
- **WARN** (30-70): Medium risk, additional review
- **BLOCK** (> 70): High risk, mandatory fixes

**Key Methods**:
- `assess_risk()` - Calculate risk score
- `_make_gate_decision()` - Determine release readiness
- `_generate_recommendations()` - Create action items
- `get_overall_assessment()` - Aggregate results

### 6. Release Outputs & Gates
**Diagram Component**: Release Outputs & Gates (Release Notes, Security Report, CI/CD Gates)
**Implementation**: `modules/report_generator.py`

**Report Generator** (`report_generator.py`):
- Creates comprehensive markdown reports
- Includes executive summary
- Provides detailed file-by-file analysis
- Lists all changes and impacts
- Generates recommendations
- Formats gate decisions

**Output Structure**:
1. Executive Summary
2. Input Sources Inventory
3. Detailed File Analysis
4. Change Statistics
5. Risk Assessments
6. Overall Recommendations
7. Conclusion with Next Steps

### 7. Automated Insights & Documentation
**Diagram Component**: Bottom banner (Release Notes, Security Findings, Component Docs, Release Checklist)
**Implementation**: All modules contribute to comprehensive output

**Generated Artifacts**:
- Modified Python files (`outputs/modified_code/`)
- Comprehensive reports (`outputs/reports/`)
- Change diffs and statistics
- Risk assessments
- Test recommendations
- Security findings

## Data Flow

```
1. USER INPUT
   ↓
2. FILE INGESTION
   ├─ Python files → AST parsing
   └─ Documents → Text extraction
   ↓
3. STATIC ANALYSIS
   ├─ Complexity calculation
   ├─ Issue detection
   └─ Structure analysis
   ↓
4. AI PROCESSING
   ├─ Query interpretation
   ├─ Code modification
   └─ Explanation generation
   ↓
5. CHANGE DETECTION
   ├─ Diff generation
   └─ Statistics calculation
   ↓
6. RISK ASSESSMENT
   ├─ Multi-factor scoring
   └─ Gate decision
   ↓
7. REPORT GENERATION
   ├─ Modified code output
   └─ Comprehensive report
   ↓
8. RELEASE DECISION
   └─ PASS/WARN/BLOCK
```

## Configuration System

**File**: `config/settings.py`

Centralized configuration for:
- Directory paths
- Risk thresholds and weights
- Complexity thresholds
- AI model settings
- Gate decision boundaries

## Execution Flow

**Main Orchestrator**: `main.py`

```python
1. Print header and initialize
2. Check input directory
3. PHASE 1: Ingestion
   - Read Python files
   - Parse documentation
   - Get user query
4. PHASE 2: Static Analysis
   - Analyze each file
   - Calculate metrics
   - Detect issues
5. PHASE 3: AI Modification
   - Build context
   - Call Claude API
   - Generate improvements
6. PHASE 4: Change Detection
   - Compare versions
   - Calculate diffs
   - Track statistics
7. PHASE 5: Risk Assessment
   - Score each file
   - Make gate decisions
   - Generate recommendations
8. PHASE 6: Output Generation
   - Write modified files
   - Create report
   - Display summary
```

## Key Design Patterns

### 1. Pipeline Pattern
Sequential processing stages with clear inputs/outputs

### 2. Strategy Pattern
Risk assessment uses multiple strategies (complexity, volume, criticality)

### 3. Builder Pattern
Report generation builds comprehensive documents incrementally

### 4. Factory Pattern
Analysis results created through standardized factory methods

### 5. Observer Pattern
Each stage observes and reacts to previous stage outputs

## Extensibility Points

The system is designed for easy extension:

1. **New Analyzers**: Add to `modules/code_analyzer.py`
2. **Custom Risk Factors**: Modify `modules/risk_assessor.py`
3. **Additional File Types**: Extend `utils/` parsers
4. **New Report Formats**: Add to `modules/report_generator.py`
5. **Different AI Models**: Configure in `config/settings.py`

## Performance Considerations

- **AST Caching**: Parsed ASTs stored in memory
- **Incremental Processing**: File-by-file analysis
- **Lazy Loading**: Documents loaded on demand
- **Stream Processing**: Large files handled efficiently

## Error Handling Strategy

1. **Graceful Degradation**: Continue on non-critical failures
2. **Detailed Logging**: Track all errors and warnings
3. **User Feedback**: Clear error messages
4. **Recovery Options**: Suggest fixes for common issues

## Security Considerations

- **API Key Management**: Environment variable based
- **Input Validation**: File type and path checks
- **Output Sanitization**: Safe file writing
- **Sandboxed Execution**: No arbitrary code execution

## Testing Strategy

For a production system, implement:

1. **Unit Tests**: Each module independently
2. **Integration Tests**: Pipeline end-to-end
3. **Regression Tests**: Known inputs/outputs
4. **Performance Tests**: Large file handling
5. **Security Tests**: Vulnerability scanning

## Future Enhancements

Aligned with production requirements:

1. **Multi-Language Support**: Java, JavaScript, Go
2. **Real CI/CD Integration**: Jenkins, GitHub Actions
3. **Database Backend**: Historical analysis storage
4. **Web Interface**: Browser-based UI
5. **Collaboration Features**: Team reviews
6. **Advanced Security**: OWASP integration
7. **ML Models**: Custom trained models
8. **Metrics Dashboard**: Real-time monitoring

## Conclusion

This implementation provides a complete, modular prototype of the IRMS system shown in the architecture diagram. Each component maps directly to diagram elements while maintaining clean separation of concerns and extensibility for future enhancements.

---

For implementation details, see individual module documentation in the source code.
