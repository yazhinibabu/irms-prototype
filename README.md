
# 🔍 Intelligent Release Management Scanner (IRMS)

**AI-Powered Code Analysis & Risk Assessment for Safer Software Releases**

IRMS is an intelligent release management system that combines static code analysis, AI-driven improvements, and multi-factor risk assessment to automate release decisions with **PASS/WARN/BLOCK** gates.

<img width="1918" height="878" alt="image" src="https://github.com/user-attachments/assets/6bb6d870-50f5-467b-8593-1bfa3fb8b2d0" />

<img width="1918" height="872" alt="image" src="https://github.com/user-attachments/assets/f7547212-1a36-4495-8e8c-9dec5ea68ed1" />

<img width="1918" height="903" alt="image" src="https://github.com/user-attachments/assets/8fc9ee63-fd3e-4c03-94ed-fb0899b572be" />



![IRMS Demo](docs/demo-screenshot.png)
*Clean UI for code analysis and risk assessment*

---

## ✨ Features

- 🔍 **Static Code Analysis** - Cyclomatic complexity, maintainability index, code smell detection
- 🤖 **AI-Powered Improvements** - Google Gemini suggests code enhancements based on natural language queries
- 📊 **Risk Assessment** - Multi-factor scoring (complexity, change volume, critical functions, issue severity)
- 🚦 **Release Gates** - Automated PASS/WARN/BLOCK decisions for deployment pipelines
- 📈 **Change Tracking** - Detailed diffs with line-by-line statistics
- 📄 **Comprehensive Reports** - Markdown and PDF reports with actionable recommendations
- 🎨 **Modern UI** - Clean Streamlit interface with interactive visualizations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini (free tier available)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/intelligent-release-management-scanner.git
cd intelligent-release-management-scanner

# Install dependencies
pip install -r requirements.txt

# Set up your Google API key
export GOOGLE_API_KEY='your-api-key-here'
# Get your free key at: https://makersuite.google.com/app/apikey
```

### Run the UI
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Run CLI Demo
```bash
python demo.py
```

---

## 📖 Usage

### Web UI Workflow

1. **Upload Files**
   - Upload Python source files (.py)
   - Optionally upload documentation (requirements, specs)

2. **Describe Changes**
   - Enter a natural language query (e.g., "Add error handling and type hints")

3. **Run Analysis**
   - Click "Run IRMS Analysis"
   - Wait for pipeline to complete (~30 seconds)

4. **Review Results**
   - View overall gate decision (PASS/WARN/BLOCK)
   - Check risk score (0-100)
   - See detailed file-by-file analysis
   - Review AI-suggested changes

5. **Download Outputs**
   - Modified Python files
   - Comprehensive report (Markdown or PDF)

### CLI Workflow
```bash
# Place files in inputs/code/
cp your_file.py inputs/code/

# Run with custom query
python main.py
# Enter: "Add comprehensive error handling"

# Check outputs
cat outputs/reports/IRMS_Report_*.md
cat outputs/modified_code/your_file.py
```

---

## 🏗️ Architecture

### Pipeline Stages
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Ingestion  │───▶│   Analysis   │───▶│ AI Engine   │
│  & Parsing  │    │  (Static)    │    │  (Gemini)   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Report    │◀───│     Risk     │◀───│   Change    │
│  Generator  │    │  Assessment  │    │  Detection  │
└─────────────┘    └──────────────┘    └─────────────┘
```

### Core Modules

| Module | Responsibility | Key Metrics |
|--------|----------------|-------------|
| **FileIngestion** | Parse Python files & docs | AST parsing, PDF extraction |
| **CodeAnalyzer** | Static analysis | Complexity, maintainability, issues |
| **AIEngine** | AI-driven improvements | Gemini API integration |
| **ChangeDetector** | Track modifications | Line diffs, statistics |
| **RiskAssessor** | Calculate risk score | 4-factor weighted scoring |
| **ReportGenerator** | Create outputs | Markdown/PDF reports |

---

## 📊 Risk Assessment

### Risk Formula
```python
total_risk = (
    0.30 × complexity_risk +
    0.20 × change_volume_risk +
    0.30 × critical_function_risk +
    0.20 × issue_severity_risk
) × 100
```

### Gate Decisions

| Risk Score | Gate Decision | Action |
|------------|---------------|--------|
| 0-30 | ✅ **PASS** | Low risk - standard review |
| 30-70 | ⚠️ **WARN** | Medium risk - additional review |
| 70-100 | 🛑 **BLOCK** | High risk - mandatory fixes |

---

## 🛠️ Configuration

Edit `config/settings.py` to customize:
```python
# AI Model
AI_MODEL = "models/gemini-2.5-flash"  # Free tier

# Risk Thresholds
RISK_GATES = {
    'PASS': 30,
    'WARN': 70,
    'BLOCK': 100
}

# Risk Weights (must sum to 1.0)
RISK_WEIGHTS = {
    'complexity_change': 0.3,
    'lines_changed': 0.2,
    'critical_functions': 0.3,
    'security_issues': 0.2
}
```

---

## 📁 Project Structure
```
intelligent-release-management-scanner/
├── app.py                    # Streamlit UI
├── main.py                   # CLI interface
├── demo.py                   # Automated demo
├── requirements.txt          # Dependencies
├── README.md                 # This file
│
├── config/
│   └── settings.py           # Configuration
│
├── modules/
│   ├── ingestion.py          # File parsing
│   ├── code_analyzer.py      # Static analysis
│   ├── ai_engine.py          # AI integration
│   ├── change_detector.py    # Diff tracking
│   ├── risk_assessor.py      # Risk scoring
│   └── report_generator.py   # Report creation
│
├── utils/
│   ├── pdf_parser.py         # PDF text extraction
│   └── ast_helper.py         # AST utilities
│
├── inputs/
│   ├── code/                 # Python source files
│   └── docs/                 # Documentation
│
└── outputs/
    ├── modified_code/        # AI-improved code
    └── reports/              # Analysis reports
```

---

## 🧪 Example Use Cases

### 1. Code Quality Improvement
```
Query: "Add docstrings and type hints to all functions"
Result: AI adds comprehensive documentation and PEP 484 type annotations
```

### 2. Error Handling Enhancement
```
Query: "Add try-except blocks and logging for error handling"
Result: AI wraps risky operations with proper exception handling
```

### 3. Security Hardening
```
Query: "Add input validation and sanitization"
Result: AI adds validation checks and flags security concerns
```

### 4. Performance Optimization
```
Query: "Optimize code for better performance"
Result: AI suggests algorithmic improvements and refactoring
```

---


### Development Setup


## 🐛 Known Limitations

- **Python-only**: Currently supports Python files only
- **Basic SAST**: Pattern-based detection (not enterprise-grade)
- **No Auth**: Prototype-level (no user authentication)
- **Single-process**: Not optimized for 1000+ files
- **AI Dependency**: Requires Google API key (free tier available)



##  Contact

**Your Name**  
- GitHub: https://github.com/yazhinibabu
- LinkedIn: https://www.linkedin.com/in/yazhini-babu/
- Email: shakthiyazhinibabu@gmail.com


#python
#ai
#code-analysis
#release-management
#static-analysis
#gemini
#risk-assessment
#code-quality
#ci-cd
#streamlit
#automation
#machine-learning
#devops
#software-engineering
#code-review
