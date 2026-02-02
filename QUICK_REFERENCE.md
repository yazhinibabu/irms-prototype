# IRMS Quick Reference Card

## 🚀 Getting Started (3 Steps)

### 1. Get FREE API Key
Visit: **https://makersuite.google.com/app/apikey**
- Sign in with Google
- Click "Create API Key"
- Copy your key (AIzaSy...)

### 2. Set Environment Variable
```bash
export GOOGLE_API_KEY='your-key-here'
```

### 3. Run IRMS
```bash
pip install -r requirements.txt
python demo.py
```

## 📁 File Structure

```
irms_prototype/
├── main.py              # Run this for interactive mode
├── demo.py              # Run this for demo with samples
├── inputs/
│   ├── code/           # PUT YOUR .py FILES HERE
│   └── docs/           # PUT YOUR .pdf/.txt FILES HERE
└── outputs/
    ├── modified_code/  # YOUR IMPROVED CODE HERE
    └── reports/        # YOUR ANALYSIS REPORTS HERE
```

## 🎯 How to Use

### Quick Demo (Sample Files Included):
```bash
python demo.py
```

### With Your Own Files:
```bash
# 1. Copy your Python files
cp your_file.py inputs/code/

# 2. Run IRMS
python main.py

# 3. Enter your request when prompted, e.g.:
#    "Add error handling and logging"
#    "Improve code quality and add docstrings"
#    "Optimize performance"
```

## 💡 Example Queries

| Query | What It Does |
|-------|--------------|
| "Add error handling" | Adds try-except blocks |
| "Add docstrings" | Documents all functions |
| "Add type hints" | Adds Python type annotations |
| "Improve code quality" | General improvements |
| "Optimize performance" | Speed optimizations |
| "Add logging" | Adds logging statements |
| "Add input validation" | Validates function inputs |

## 📊 Understanding the Output

### Risk Scores (0-100):
- **0-30**: ✅ PASS - Low risk, safe to deploy
- **30-70**: ⚠️ WARN - Medium risk, review recommended  
- **70-100**: 🛑 BLOCK - High risk, fixes required

### Output Files:
1. **Modified Code** - In `outputs/modified_code/`
2. **Analysis Report** - In `outputs/reports/IRMS_Report_*.md`

## 🔧 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (Linux/Mac)
export GOOGLE_API_KEY='your-key'

# Set API key (Windows)
set GOOGLE_API_KEY=your-key

# Run demo
python demo.py

# Run with your files
python main.py

# View report
cat outputs/reports/IRMS_Report_*.md

# View modified code
cat outputs/modified_code/your_file.py
```

## ⚙️ Configuration

Edit `config/settings.py` to customize:
- Risk thresholds
- Complexity limits
- AI model settings

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No Python files found" | Add .py files to `inputs/code/` |
| "API key not found" | Set `GOOGLE_API_KEY` environment variable |
| "Module not found" | Run: `pip install -r requirements.txt` |
| "Permission denied" | Run from project directory |

## 📚 Documentation Files

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide
- **GEMINI_SETUP.md** - Detailed API setup
- **ARCHITECTURE.md** - System architecture
- **INTERVIEW_GUIDE.md** - Interview preparation

## 🎓 For Interviews

**Key Points to Mention:**
1. Modular architecture with 6 core components
2. AI-powered code analysis using Gemini
3. Multi-factor risk assessment
4. Comprehensive reporting
5. Production-ready design patterns

**Demo Script:**
```bash
# Show structure
tree -L 2 irms_prototype/

# Run demo
python demo.py

# Show results
cat outputs/reports/IRMS_Report_*.md
```

## 💰 Costs

**FREE TIER:**
- 15 requests/minute
- 1M tokens/day
- Perfect for development and demos

**Your IRMS usage:** ~1-5 requests per run = **FREE** ✅

## 🔗 Useful Links

- Get API Key: https://makersuite.google.com/app/apikey
- Gemini Docs: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api/python

## ⚡ Quick Tips

1. **Start with demo.py** to see how it works
2. **Read GEMINI_SETUP.md** for detailed API setup
3. **Use .env file** to store your API key permanently
4. **Check outputs/** directory after each run
5. **Review modified code** before using it

---

**Need Help?** Check GEMINI_SETUP.md or README.md

**Ready to Start?**
```bash
python demo.py
```

🚀 Happy coding!
