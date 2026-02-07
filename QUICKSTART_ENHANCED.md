# IRMS Enhanced - Quick Start Guide

## What's New? 🚀

Your IRMS prototype now has **production-ready features**:

1. ✅ **Project-Level Ingestion** - Scan entire projects recursively
2. ✅ **Batch Processing** - Handle 100+ files efficiently  
3. ✅ **Optional AI** - Works without AI, graceful fallback

---

## Quick Test (2 minutes)

### Test 1: Backward Compatible (Original Way)
```bash
# Works exactly as before - no changes needed!
python main.py
```

### Test 2: Scan Entire Project
```bash
# NEW: Scan your whole project
python main.py --project-path /path/to/your/project

# Example: Scan current directory
python main.py --project-path .
```

### Test 3: Skip AI (Static Analysis Only)
```bash
# NEW: Works without API key
python main.py --project-path . --no-ai
```

---

## Installation

### 1. Copy Enhanced Files

Replace these files in your project:
```
✓ config/settings.py          (NEW)
✓ modules/ingestion.py         (ENHANCED)
✓ modules/ai_engine.py         (ENHANCED)
✓ main.py                      (ENHANCED)
```

Keep these files (unchanged):
```
✓ modules/code_analyzer.py
✓ modules/change_detector.py
✓ modules/risk_assessor.py
✓ modules/report_generator.py
✓ demo.py
✓ app.py
```

### 2. No New Dependencies

Same requirements.txt - no new packages needed!

---

## New Command-Line Options

```bash
# Basic usage (unchanged)
python main.py

# NEW: Scan entire project
python main.py --project-path /path/to/project

# NEW: With custom query
python main.py --project-path . --query "Add error handling"

# NEW: Skip AI processing
python main.py --no-ai

# NEW: Custom batch size
python main.py --batch-size 20

# NEW: Non-interactive (for CI/CD)
python main.py --project-path . --query "Check quality" --non-interactive
```

---

## Configuration

Edit `config/settings.py`:

### For Small Projects (<50 files)
```python
BATCH_SIZE = 50
ENABLE_BATCH_PROCESSING = False
```

### For Large Projects (200+ files)
```python
BATCH_SIZE = 10
ENABLE_BATCH_PROCESSING = True
CLEAR_CACHE_BETWEEN_BATCHES = True
```

### Disable AI (Static Analysis Only)
```python
ENABLE_AI = False
```

---

## Usage Examples

### Example 1: Analyze Django Project
```bash
python main.py --project-path ~/my-django-app
# Scans all .py files recursively
# Respects .gitignore
# Processes in batches
```

### Example 2: Quick Scan Without AI
```bash
python main.py --project-path . --no-ai
# Fast static analysis only
# No API key needed
```

### Example 3: CI/CD Integration
```yaml
# .github/workflows/code-quality.yml
- name: IRMS Analysis
  run: |
    python main.py \
      --project-path . \
      --query "Check code quality" \
      --non-interactive \
      --no-ai
```

---

## What Happens with Batch Processing?

### Before (Original)
```
Processing 100 files...
[waits forever, might crash]
```

### After (Enhanced)
```
Processing batch 1/10 (10 files)...
✓ Batch 1 complete
Processing batch 2/10 (10 files)...
✓ Batch 2 complete
...
✓ All batches complete!
```

---

## Project Scanning Features

### Respects .gitignore
```
# Your .gitignore
__pycache__/
*.pyc
venv/

# IRMS automatically skips these!
```

### Default Ignore Patterns
Already configured in `settings.py`:
- `__pycache__`, `.git`, `node_modules`
- `venv`, `env`, `.venv`  
- `build`, `dist`, `*.egg-info`
- Your `outputs` directory

### File Size Limits
```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB default
# Prevents processing huge files
```

---

## AI Fallback Behavior

### Before (Original)
```
AI API fails → Pipeline crashes 💥
```

### After (Enhanced)
```
AI API fails → Uses original code ✓
System continues → Report generated ✓
```

### Fallback Modes

**Mode 1: No API Key**
```bash
$ python main.py --project-path .
⚠ GOOGLE_API_KEY not set. AI features disabled (fallback mode).
ℹ AI engine disabled or unavailable
[continues with static analysis only]
```

**Mode 2: API Failure**
```bash
⚠ API call failed (attempt 1/3). Retrying in 2s...
⚠ API call failed (attempt 2/3). Retrying in 4s...
⚠ AI unavailable for file.py, using original code
[continues processing other files]
```

**Mode 3: Explicit Disable**
```bash
$ python main.py --no-ai
⚠ AI processing disabled (--no-ai flag)
[static analysis only]
```

---

## Troubleshooting

### Issue: "No Python files found"
**Solution:** 
```bash
# Make sure path is correct
python main.py --project-path /correct/path

# Or use absolute path
python main.py --project-path $(pwd)
```

### Issue: "Permission denied" on some files
**Solution:** Already handled! IRMS skips permission-denied files automatically.

### Issue: Processing too slow
**Solution:** 
```bash
# Reduce batch size for faster iteration
python main.py --batch-size 5

# Or skip AI for speed
python main.py --no-ai
```

### Issue: Out of memory with large project
**Solution:**
```python
# In config/settings.py
CLEAR_CACHE_BETWEEN_BATCHES = True
BATCH_SIZE = 5  # Smaller batches
```

---

## Performance Comparison

### Original Version
- ❌ Scans only `inputs/code/` directory
- ❌ Processes all files at once
- ❌ Memory grows with file count
- ❌ Crashes if AI fails

### Enhanced Version  
- ✅ Scans entire projects
- ✅ Processes in batches
- ✅ Constant memory usage
- ✅ Graceful AI fallback
- ✅ Progress indicators
- ✅ Rate limiting

---

## Migration Checklist

- [ ] Copy new `config/settings.py`
- [ ] Replace `modules/ingestion.py`
- [ ] Replace `modules/ai_engine.py`
- [ ] Replace `main.py`
- [ ] Test with `python main.py` (should work as before)
- [ ] Test with `python main.py --project-path .`
- [ ] Test with `python main.py --no-ai`
- [ ] Update your CI/CD scripts (optional)

---

## Next Steps

1. **Try it out:**
   ```bash
   python main.py --project-path .
   ```

2. **Read full documentation:**
   - `CHANGES.md` - Detailed technical changes
   - `README.md` - General usage
   - `config/settings.py` - All configuration options

3. **Optional enhancements:**
   - Update `app.py` for web UI project scanning
   - Update `demo.py` for batch processing demo
   - Add custom ignore patterns for your project

---

## Support

**Questions?** Check:
1. `CHANGES.md` - Detailed implementation guide
2. `config/settings.py` - Configuration reference
3. Command-line help: `python main.py --help`

---

**Ready to go!** 🚀

Your IRMS is now production-ready for:
- Large projects (100+ files)
- CI/CD pipelines
- Environments without AI API keys
- Real-world software development workflows

Happy scanning! ✨
