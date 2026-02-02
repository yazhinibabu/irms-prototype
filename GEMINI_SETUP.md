# Google Gemini API Setup Guide

## Why Gemini 1.5 Flash?

✅ **FREE Tier** - No credit card required for getting started
✅ **Generous Limits** - 15 requests per minute, 1 million tokens per day (free tier)
✅ **Fast** - Optimized for speed
✅ **Powerful** - Excellent code understanding and generation

## Step-by-Step Setup

### 1. Get Your Free API Key

**Visit**: https://makersuite.google.com/app/apikey

Or: https://aistudio.google.com/app/apikey

**Steps:**
1. Sign in with your Google account (any Gmail account works)
2. Click **"Create API Key"** button
3. Choose **"Create API key in new project"** (if first time)
4. Copy the API key (starts with `AIza...`)
5. Keep it secure - treat it like a password!

### 2. Set the Environment Variable

#### Linux/Mac:
```bash
export GOOGLE_API_KEY='AIzaSy...-your-actual-key'
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GOOGLE_API_KEY="AIzaSy...-your-actual-key"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows Command Prompt:
```cmd
set GOOGLE_API_KEY=AIzaSy...-your-actual-key
```

#### Windows PowerShell:
```powershell
$env:GOOGLE_API_KEY='AIzaSy...-your-actual-key'
```

To make it permanent on Windows:
```cmd
setx GOOGLE_API_KEY "AIzaSy...-your-actual-key"
```

#### Using .env File (Recommended):
Create a file named `.env` in the `irms_prototype` directory:
```
GOOGLE_API_KEY=AIzaSy...-your-actual-key
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to your code (already included in IRMS):
```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Verify Setup

Test that everything works:

```bash
python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.environ.get('GOOGLE_API_KEY')); print('✓ API key configured successfully!')"
```

If you see: `✓ API key configured successfully!` - you're all set! 🎉

## Free Tier Limits

Gemini 1.5 Flash **FREE** tier includes:
- **15 requests per minute (RPM)**
- **1 million tokens per day**
- **1,500 requests per day**

For IRMS usage:
- Each file analysis = ~1-2 requests
- Average IRMS run = 1-3 files
- You can run IRMS **hundreds of times per day** for FREE!

## Upgrading (Optional)

If you need more capacity:
- **Pay-as-you-go**: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Still much cheaper than other AI APIs!
- Enable billing at: https://console.cloud.google.com/billing

## Troubleshooting

### Error: "API key not found"
**Solution**: Make sure you've set the environment variable:
```bash
echo $GOOGLE_API_KEY  # Linux/Mac
echo %GOOGLE_API_KEY%  # Windows CMD
```

### Error: "Permission denied" or "API not enabled"
**Solution**: Enable the Generative Language API:
1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click "Enable"

### Error: "Quota exceeded"
**Solution**: You've hit the free tier limit. Wait an hour or:
- Reduce number of files analyzed at once
- Enable billing for higher limits

### Error: "Invalid API key"
**Solution**: 
- Check for typos in your API key
- Regenerate key at: https://makersuite.google.com/app/apikey
- Make sure there are no extra spaces or quotes

## Security Best Practices

1. **Never commit API keys to Git**
   Add to `.gitignore`:
   ```
   .env
   *.env
   ```

2. **Use environment variables** instead of hardcoding

3. **Restrict your API key** (optional):
   - Go to Google Cloud Console
   - Set API restrictions to only allow Generative Language API
   - Set IP restrictions if needed

4. **Rotate keys regularly** if you suspect exposure

## Testing Your Setup

Quick test:
```python
import google.generativeai as genai
import os

# Configure
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

# Test
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Say hello!')
print(response.text)
```

If this prints a greeting, your setup is perfect! ✅

## IRMS-Specific Setup

After setting up your API key:

```bash
# 1. Navigate to IRMS directory
cd irms_prototype

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify API key is set
python -c "import os; print('Key set!' if os.environ.get('GOOGLE_API_KEY') else 'Key NOT set')"

# 4. Run demo
python demo.py
```

## Comparison: Gemini vs Other APIs

| Feature | Gemini 1.5 Flash (FREE) | Claude | GPT-4 |
|---------|-------------------------|---------|-------|
| Cost | FREE (with limits) | Pay-per-use | Pay-per-use |
| Free Tier | ✅ 1M tokens/day | ❌ None | ❌ Limited |
| Speed | Very Fast | Fast | Medium |
| Code Quality | Excellent | Excellent | Excellent |
| Setup | Easy | Easy | Medium |

## Need Help?

- **Gemini Docs**: https://ai.google.dev/docs
- **API Reference**: https://ai.google.dev/api/python
- **Community**: https://developers.googleblog.com/

## Summary

✓ Get free API key at: https://makersuite.google.com/app/apikey
✓ Set environment variable: `export GOOGLE_API_KEY='your-key'`
✓ Install dependencies: `pip install -r requirements.txt`
✓ Run IRMS: `python demo.py`

You're ready to go! 🚀
