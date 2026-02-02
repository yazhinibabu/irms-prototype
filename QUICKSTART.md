# IRMS Quick Start Guide

## Setup Instructions

### 1. Install Dependencies
```bash
cd irms_prototype
pip install -r requirements.txt
```

### 2. Set API Key (FREE)

Get your free Google API key at: https://makersuite.google.com/app/apikey

```bash
# Linux/Mac
export GOOGLE_API_KEY='your-api-key-here'

# Windows
set GOOGLE_API_KEY=your-api-key-here
```

Or create a `.env` file in the project root:
```
GOOGLE_API_KEY=your-api-key-here
```

### 3. Verify Installation
```bash
python -c "import google.generativeai; print('Setup successful!')"
```

## Running the Demo

A sample calculator file is provided for testing:

```bash
python demo.py
```

This will:
- Analyze `sample_calculator.py`
- Apply improvements based on requirements
- Generate risk assessment
- Create comprehensive report

## Running with Your Own Files

### 1. Add Your Files
```bash
# Copy Python files
cp your_project/*.py inputs/code/

# Copy documentation (optional)
cp your_docs/*.pdf inputs/docs/
cp your_docs/*.txt inputs/docs/
```

### 2. Run IRMS
```bash
python main.py
```

### 3. Enter Your Query
When prompted, describe what you want:

Examples:
- "Add error handling and logging"
- "Improve code quality and add docstrings"
- "Optimize performance and reduce complexity"
- "Add type hints and input validation"
- "Refactor to follow best practices"

### 4. Review Results
```bash
# View report
cat outputs/reports/IRMS_Report_*.md

# Check modified code
ls outputs/modified_code/
```

## Understanding the Output

### Report Structure
1. **Executive Summary** - Overall status and risk score
2. **Input Sources** - Files analyzed
3. **Detailed File Analysis** - Per-file breakdown
4. **Overall Recommendations** - Action items
5. **Conclusion** - Gate decision and next steps

### Gate Decisions
- **✅ PASS** - Low risk (< 30), safe to proceed
- **⚠️ WARN** - Medium risk (30-70), review recommended
- **🛑 BLOCK** - High risk (> 70), fixes required

### Risk Components
- **Complexity Risk** - Code complexity changes
- **Change Volume Risk** - Amount of code modified
- **Critical Function Risk** - Changes to security/core functions
- **Issue Severity Risk** - Severity of detected issues

## Customization

Edit `config/settings.py` to adjust:
- Risk thresholds
- Complexity limits
- AI model settings

## Troubleshooting

**Problem**: "No Python files found"
- Solution: Add `.py` files to `inputs/code/`

**Problem**: "API key not found"
- Solution: Set `GOOGLE_API_KEY` environment variable
- Get free key at: https://makersuite.google.com/app/apikey

**Problem**: "Module not found"
- Solution: Run from project root: `cd irms_prototype && python main.py`

**Problem**: "Import errors"
- Solution: Install dependencies: `pip install -r requirements.txt`

## Architecture Overview

```
                    IRMS Pipeline
                    
Input → Ingest → Analyze → AI Modify → Detect Changes → Assess Risk → Report
  |        |        |          |             |              |           |
Files   Parse    Static    Claude AI      Diff          Score       Output
        AST      Analysis   Engine        Tracking      Compute     Generate
```

## Example Workflow

```bash
# 1. Setup
export GOOGLE_API_KEY='your-free-api-key'

# 2. Add files
cp my_app.py inputs/code/

# 3. Run
python main.py

# 4. Enter query
> Add comprehensive error handling and logging

# 5. Review
cat outputs/reports/IRMS_Report_*.md
```

## Tips for Best Results

1. **Specific Queries** - Be clear about what you want
2. **Context Documents** - Add requirements/specs to `inputs/docs/`
3. **Review Output** - Always review AI-generated changes
4. **Iterative Process** - Run multiple times with different queries
5. **Version Control** - Keep original files in version control

## Next Steps

After running IRMS:

1. Review the comprehensive report
2. Examine modified code files
3. Test the changes
4. Address any BLOCK or WARN decisions
5. Integrate approved changes

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review module documentation in code
3. Consult the architecture diagram
4. Read inline code comments

---

Happy analyzing! 🚀
