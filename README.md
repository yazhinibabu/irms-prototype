# Intelligent Release Management Scanner (IRMS)

A prototype system for intelligent code analysis, modification, and release management using AI-assisted workflows.

## Overview

IRMS is an end-to-end Python application that ingests source code and supporting documentation, applies AI-powered analysis and modifications based on natural language queries, and generates comprehensive release-ready outputs with risk assessments.

## Architecture

The system follows the pipeline shown in the architecture diagram:

```
Input Sources → Ingestion & Parsing → Security & Change Analysis → 
Product Intelligence Model → Release Analysis & Reporting → Release Outputs & Gates
```

### Key Components

1. **File Ingestion** (`modules/ingestion.py`)
   - Reads Python source files
   - Extracts text from PDF and text documents
   - Parses code into Abstract Syntax Trees (AST)

2. **Static Code Analyzer** (`modules/code_analyzer.py`)
   - Calculates complexity metrics (cyclomatic complexity, maintainability index)
   - Detects code issues and patterns
   - Analyzes code structure (functions, classes, imports)

3. **AI Engine** (`modules/ai_engine.py`)
   - Uses Claude API for intelligent code analysis
   - Applies modifications based on user queries
   - Generates explanations for all changes

4. **Change Detector** (`modules/change_detector.py`)
   - Tracks differences between original and modified code
   - Generates unified diffs
   - Calculates change statistics

5. **Risk Assessor** (`modules/risk_assessor.py`)
   - Scores risk based on multiple factors
   - Makes gate decisions (PASS/WARN/BLOCK)
   - Generates recommendations

6. **Report Generator** (`modules/report_generator.py`)
   - Creates comprehensive markdown reports
   - Includes all analysis results and recommendations
   - Provides executive summary and detailed breakdowns

## Installation

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini (FREE tier available)

### Setup

1. Clone or download the project:
```bash
cd irms_prototype
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google API key (FREE):

**Get Your Free API Key:**
- Go to: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy your key

**Set the environment variable:**
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

## Usage

### 1. Prepare Your Inputs

Place your files in the appropriate directories:

- **Python source files**: `inputs/code/`
- **Supporting documents** (PDF/text): `inputs/docs/`

Example:
```bash
inputs/
├── code/
│   ├── my_script.py
│   └── utils.py
└── docs/
    ├── requirements.pdf
    └── specifications.txt
```

### 2. Run IRMS

Execute the main script:
```bash
python main.py
```

The system will:
1. Ingest all files
2. Prompt you for a natural language query (e.g., "Add error handling and improve code quality")
3. Analyze the code
4. Apply AI-powered modifications
5. Assess risks
6. Generate outputs

### 3. Review Outputs

Check the `outputs/` directory:

- **Modified code**: `outputs/modified_code/`
- **Comprehensive report**: `outputs/reports/IRMS_Report_[timestamp].md`

## Example Workflow

```bash
# 1. Add your Python files
cp my_project/*.py inputs/code/

# 2. Add documentation (optional)
cp requirements.pdf inputs/docs/

# 3. Run IRMS
python main.py

# When prompted, enter your request:
# "Add comprehensive error handling and logging to all functions"

# 4. Review results
cat outputs/reports/IRMS_Report_*.md
```

## Configuration

Edit `config/settings.py` to customize:

- Risk thresholds and weights
- Complexity thresholds
- AI model settings
- Directory paths

## Key Features

### Static Analysis
- Cyclomatic complexity calculation
- Maintainability index scoring
- Code issue detection (missing docstrings, bare excepts, etc.)
- Structure analysis (functions, classes, imports)

### AI-Powered Modifications
- Natural language query processing
- Context-aware code improvements
- Detailed change explanations
- Best practices enforcement

### Risk Assessment
- Multi-factor risk scoring
- Automated gate decisions (PASS/WARN/BLOCK)
- Component-level risk breakdown
- Actionable recommendations

### Comprehensive Reporting
- Executive summary
- Detailed file-by-file analysis
- Change statistics and diffs
- Risk assessments and recommendations

## Project Structure

```
irms_prototype/
├── main.py                      # Main orchestrator
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── config/
│   └── settings.py              # Configuration
├── modules/                     # Core functionality
│   ├── ingestion.py             # File reading & parsing
│   ├── code_analyzer.py         # Static analysis
│   ├── ai_engine.py             # AI modifications
│   ├── change_detector.py       # Change tracking
│   ├── risk_assessor.py         # Risk scoring
│   └── report_generator.py      # Report creation
├── utils/                       # Helper utilities
│   ├── pdf_parser.py            # PDF text extraction
│   └── ast_helper.py            # AST manipulation
├── inputs/                      # User input files
│   ├── code/                    # Python source files
│   └── docs/                    # Supporting documents
└── outputs/                     # Generated outputs
    ├── modified_code/           # Updated Python files
    └── reports/                 # Analysis reports
```

## Example Use Cases

1. **Code Quality Improvement**
   - Query: "Improve code quality and add comprehensive docstrings"
   - System adds docstrings, improves naming, refactors complex functions

2. **Error Handling Enhancement**
   - Query: "Add proper error handling with try-except blocks and logging"
   - System wraps risky operations, adds logging, handles exceptions

3. **Security Hardening**
   - Query: "Add input validation and security checks"
   - System adds validation, sanitizes inputs, flags security issues

4. **Performance Optimization**
   - Query: "Optimize code for better performance"
   - System identifies bottlenecks, suggests optimizations

5. **Technical Debt Reduction**
   - Query: "Refactor code to reduce complexity and improve maintainability"
   - System simplifies complex functions, improves structure

## Risk Gates Explained

- **PASS (< 30 risk score)**: Low risk, safe to proceed with standard review
- **WARN (30-70 risk score)**: Medium risk, additional review recommended
- **BLOCK (> 70 risk score)**: High risk, requires thorough review and fixes

## Limitations

This is a **prototype** system with the following constraints:

- No real CI/CD integration
- No commercial security scanner integration
- Limited to Python source files
- AI modifications require manual review
- Not production-ready for enterprise deployment

## Future Enhancements

Potential improvements for a production system:

- Integration with real CI/CD pipelines
- Support for multiple programming languages
- Automated test generation
- Integration with version control systems
- Real-time collaboration features
- Advanced security scanning
- Performance profiling integration

## Troubleshooting

### No Python files found
- Ensure `.py` files are in `inputs/code/`
- Check file permissions

### API key errors
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check API key permissions

### Module import errors
- Run from the project root directory
- Verify all dependencies are installed

## License

This is a prototype project for educational and demonstration purposes.

## Author

Senior Software Architect & AI Engineer

---

For questions or issues, please refer to the system architecture diagram and module documentation.
