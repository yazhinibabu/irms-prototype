"""
IRMS Configuration Settings
Enhanced with project-level ingestion, batch processing, and optional AI
"""
from pathlib import Path

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Input directories (backward compatible)
CODE_DIR = INPUTS_DIR / "code"
DOCS_DIR = INPUTS_DIR / "docs"

# Output directories
MODIFIED_CODE_DIR = OUTPUTS_DIR / "modified_code"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure directories exist
for directory in [CODE_DIR, DOCS_DIR, MODIFIED_CODE_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# PROJECT-LEVEL INGESTION (NEW)
# ============================================================================

# Enable project-level ingestion (recursive directory scanning)
ENABLE_PROJECT_INGESTION = True

# File patterns to include
INCLUDE_PATTERNS = [
    "**/*.py",      # Python files
    "**/*.txt",     # Text documents
    "**/*.md",      # Markdown documents
    "**/*.pdf",     # PDF documents
]

# Directories to ignore (similar to .gitignore)
IGNORE_DIRECTORIES = [
    "__pycache__",
    ".git",
    ".svn",
    "node_modules",
    "venv",
    "env",
    ".venv",
    ".env",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "htmlcov",
    "outputs",      # Don't scan our own outputs
]

# Files to ignore
IGNORE_FILES = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.so",
    "*.dll",
    "*.dylib",
]

# Maximum file size to process (in bytes) - 5MB default
MAX_FILE_SIZE = 5 * 1024 * 1024

# Maximum depth for directory recursion
MAX_RECURSION_DEPTH = 10

# ============================================================================
# BATCH PROCESSING (NEW)
# ============================================================================

# Enable batch processing
ENABLE_BATCH_PROCESSING = True

# Number of files to process in each batch
BATCH_SIZE = 10

# Delay between batches (seconds) - for rate limiting
BATCH_DELAY = 1.0

# Show progress indicators
SHOW_BATCH_PROGRESS = True

# ============================================================================
# AI CONFIGURATION (ENHANCED)
# ============================================================================

# AI Model selection
AI_MODEL = "models/gemini-2.5-flash"

# Enable/disable AI processing (NEW)
ENABLE_AI = True

# AI is optional - system works without it
AI_OPTIONAL = True

# Retry configuration for AI calls (NEW)
AI_MAX_RETRIES = 3
AI_RETRY_DELAY = 2.0  # seconds
AI_RETRY_BACKOFF = 2.0  # exponential backoff multiplier

# Rate limiting (NEW)
AI_RATE_LIMIT_DELAY = 1.0  # seconds between API calls
AI_MAX_REQUESTS_PER_MINUTE = 15  # Free tier limit

# Token limits
MAX_TOKENS = 4000
TEMPERATURE = 0.7

# Fallback behavior when AI fails (NEW)
AI_FALLBACK_TO_ORIGINAL = True

# ============================================================================
# RISK ASSESSMENT
# ============================================================================

# Risk component weights (must sum to 1.0)
RISK_WEIGHTS = {
    'complexity_change': 0.3,
    'lines_changed': 0.2,
    'critical_functions': 0.3,
    'security_issues': 0.2
}

# Gate decision thresholds
RISK_GATES = {
    'PASS': 30,    # 0-30: Low risk
    'WARN': 70,    # 30-70: Medium risk
    'BLOCK': 100   # 70-100: High risk
}

# ============================================================================
# CODE ANALYSIS
# ============================================================================

# Complexity thresholds
COMPLEXITY_THRESHOLD = {
    'low': 5,
    'medium': 10,
    'high': 20,
    'very_high': 30
}

# Issue severity levels
SEVERITY_LEVELS = ['info', 'low', 'medium', 'high', 'critical']

# ============================================================================
# REPORTING
# ============================================================================

# Report format
REPORT_FORMAT = "markdown"  # Options: "markdown", "pdf", "html"

# Include detailed diffs in report
INCLUDE_DIFFS_IN_REPORT = True

# Maximum diff lines to show in report
MAX_DIFF_LINES_IN_REPORT = 100

# ============================================================================
# PERFORMANCE & DEBUGGING
# ============================================================================

# Enable verbose logging
VERBOSE = True

# Enable performance profiling
ENABLE_PROFILING = False

# Cache parsed ASTs (memory vs speed tradeoff)
CACHE_ASTS = True

# Clear cache between batches (for large projects)
CLEAR_CACHE_BETWEEN_BATCHES = True