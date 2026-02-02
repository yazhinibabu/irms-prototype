"""
Configuration settings for IRMS prototype
"""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Directory paths
INPUTS_DIR = PROJECT_ROOT / "inputs"
CODE_DIR = INPUTS_DIR / "code"
DOCS_DIR = INPUTS_DIR / "docs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MODIFIED_CODE_DIR = OUTPUTS_DIR / "modified_code"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Create directories if they don't exist
for directory in [CODE_DIR, DOCS_DIR, MODIFIED_CODE_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Analysis thresholds
COMPLEXITY_THRESHOLD = {
    'low': 5,
    'medium': 10,
    'high': 20
}

# Risk scoring
RISK_WEIGHTS = {
    'complexity_change': 0.3,
    'lines_changed': 0.2,
    'critical_functions': 0.3,
    'security_issues': 0.2
}

RISK_GATES = {
    'PASS': 30,      # Risk score < 30
    'WARN': 70,      # Risk score 30-70
    'BLOCK': 100     # Risk score > 70
}

# AI Model settings
AI_MODEL = "gemini-2.5-flash"
MAX_TOKENS = 4000
TEMPERATURE = 0.7
