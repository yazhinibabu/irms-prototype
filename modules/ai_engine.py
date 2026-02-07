"""
AI-assisted code analysis and modification engine using Google Gemini
Enhanced with optional AI, rate limiting, and fallback mechanisms
"""
from typing import Dict, List, Optional, Any
import os
import time
from pathlib import Path
from typing import Optional


# Import Google Generative AI
try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. AI features disabled.")

# Try to load from .env file if present
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class AIEngine:
    """AI-powered code analysis and modification using Google Gemini."""
    
    def __init__(
        self,
        enabled: bool = True,
        optional: bool = True,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize the AI engine with Gemini API.
        
        Args:
            enabled: Enable/disable AI processing (NEW)
            optional: AI is optional - fallback to original if fails (NEW)
            max_retries: Maximum retry attempts for API calls (NEW)
            retry_delay: Delay between retries in seconds (NEW)
            rate_limit_delay: Delay between API calls for rate limiting (NEW)
        """
        self.enabled = enabled
        self.optional = optional
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        
        self.model: Optional[Any] = None
        self.conversation_history: List[Dict] = []
        self.last_api_call_time = 0
        self.api_call_count = 0
        
        # Initialize AI if enabled and available
        if self.enabled and GEMINI_AVAILABLE:
            self._initialize_ai()
        else:
            print("ℹ AI engine disabled or unavailable")
    
    def _initialize_ai(self):
        """Initialize Gemini API (NEW - separated from __init__)."""
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            if self.optional:
                print("⚠ GOOGLE_API_KEY not set. AI features disabled (fallback mode).")
                self.enabled = False
            else:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable not set. "
                    "Get your free API key at https://makersuite.google.com/app/apikey"
                )
        else:
            try:
                # Import AI_MODEL from settings
                try:
                    from config.settings import AI_MODEL, MAX_TOKENS, TEMPERATURE
                except:
                    AI_MODEL = "models/gemini-2.5-flash"
                    MAX_TOKENS = 4000
                    TEMPERATURE = 0.7
                
                genai.configure(api_key=api_key)  # type: ignore
                self.model = genai.GenerativeModel(AI_MODEL)  # type: ignore
                print("✓ AI engine initialized with Gemini")
            except Exception as e:
                if self.optional:
                    print(f"⚠ AI initialization failed: {e}. Fallback mode enabled.")
                    self.enabled = False
                else:
                    raise
    
    def _rate_limit_wait(self):
        """Implement rate limiting (NEW)."""
        elapsed = time.time() - self.last_api_call_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_api_call_time = time.time()
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff (NEW)."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠ API call failed (attempt {attempt + 1}/{self.max_retries}). "
                          f"Retrying in {delay}s... Error: {e}")
                    time.sleep(delay)
                else:
                    raise
    
    def analyze_and_modify(
        self,
        source_code: str,
        filename: str,
        user_query: str,
        static_analysis: Dict,
        context_docs: str = ""
    ) -> Dict[str, Any]:

        # 1️⃣ AI globally disabled
        if not self.enabled:
            return self._fallback_response(source_code, "AI is disabled")

        # 2️⃣ AI enabled but model not initialized
        if self.model is None:
            return self._fallback_response(
                source_code,
                "AI model is not initialized"
            )
        # 3️⃣ Rate limiting (safe now)
        self._rate_limit_wait()

        # 4️⃣ Build prompt
        prompt = self._build_analysis_prompt(
            source_code, filename, user_query, static_analysis, context_docs
        )
        
        try:
            # Call API with retry logic
            response = self._retry_with_backoff(
                self.model.generate_content, 
                prompt
            )

            if response is None:
                raise ValueError("AI response is None.")
            
            response_text = response.text
            
            if not response_text:
                raise ValueError("Received empty response from AI model.")
            
            self.api_call_count += 1
            result = self._parse_ai_response(response_text, source_code)
            return result
            
        except Exception as e:
            print(f"⚠ AI analysis error for {filename}: {e}")
            
            if self.optional:
                # Fallback to original code
                return self._fallback_response(source_code, str(e))
            else:
                # Re-raise if AI is not optional
                raise
    
    def _fallback_response(self, source_code: str, reason: str) -> Dict[str, Any]:
        """
        Generate fallback response when AI is unavailable (NEW).
        
        Args:
            source_code: Original code
            reason: Reason for fallback
            
        Returns:
            Dictionary with original code preserved
        """
        return {
            'modified_code': source_code,
            'changes_made': [],
            'explanation': f"AI analysis skipped: {reason}. Original code preserved.",
            'success': False,
            'fallback': True  # NEW flag
        }
    
    def _build_analysis_prompt(
        self,
        source_code: str,
        filename: str,
        user_query: str,
        static_analysis: Dict,
        context_docs: str
    ) -> str:
        """Build a comprehensive prompt for Gemini."""
        
        issues_summary = self._format_issues(static_analysis.get('issues', []))
        complexity_info = static_analysis.get('complexity', {})
        
        prompt = f"""You are a senior software engineer performing code review and improvement.

**File being analyzed:** {filename}

**User Request:**
{user_query}

**Original Source Code:**
```python
{source_code}
```

**Static Analysis Results:**
- Average Complexity: {complexity_info.get('average', 'N/A')}
- Maintainability Index: {static_analysis.get('metrics', {}).get('maintainability_index', 'N/A')}
- Issues Found: {len(static_analysis.get('issues', []))}

{issues_summary}

**Supporting Documentation Context:**
{context_docs if context_docs else "No additional documentation provided."}

**Your Task:**
1. Analyze the code based on the user's request: "{user_query}"
2. Identify specific improvements needed
3. Generate the complete modified Python code
4. Explain each change you made and why

**Response Format:**
Please structure your response EXACTLY as follows:

MODIFIED CODE:
```python
[Complete modified Python code here]
```

CHANGES MADE:
1. [First change description]
2. [Second change description]
...

EXPLANATION:
[Detailed explanation of your analysis and reasoning]

**Important Guidelines:**
- Maintain the original functionality unless the user explicitly requests changes
- Follow Python best practices (PEP 8)
- Add proper error handling where appropriate
- Include docstrings for functions/classes if missing
- Optimize for readability and maintainability
- Be specific about what you changed and why
"""
        
        return prompt
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format static analysis issues for the prompt."""
        if not issues:
            return "No issues detected."
        
        formatted = "**Issues Detected:**\n"
        for i, issue in enumerate(issues[:10], 1):
            formatted += f"{i}. Line {issue['line']}: {issue['message']} (Severity: {issue['severity']})\n"
        
        if len(issues) > 10:
            formatted += f"... and {len(issues) - 10} more issues.\n"
        
        return formatted
    
    def _parse_ai_response(self, response_text: str, original_code: str) -> Dict:
        """Parse Gemini's response to extract code and explanations."""
        result = {
            'modified_code': original_code,
            'changes_made': [],
            'explanation': '',
            'success': True,
            'fallback': False
        }
        
        if 'MODIFIED CODE:' in response_text:
            code_section = response_text.split('MODIFIED CODE:')[1]
            if '```python' in code_section:
                code_parts = code_section.split('```python')[1].split('```')[0]
                result['modified_code'] = code_parts.strip()
            elif '```' in code_section:
                code_parts = code_section.split('```')[1].split('```')[0]
                result['modified_code'] = code_parts.strip()
        
        if 'CHANGES MADE:' in response_text:
            try:
                changes_section = response_text.split('CHANGES MADE:')[1].split('EXPLANATION:')[0]
            except:
                changes_section = response_text.split('CHANGES MADE:')[1]
            
            changes = [
                line.strip() for line in changes_section.strip().split('\n')
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))
            ]
            result['changes_made'] = changes
        
        if 'EXPLANATION:' in response_text:
            explanation_section = response_text.split('EXPLANATION:')[1]
            result['explanation'] = explanation_section.strip()
        else:
            result['explanation'] = response_text
        
        return result
    
    def get_impact_summary(
        self,
        original_code: str,
        modified_code: str,
        changes_made: List[str]
    ) -> Dict:
        """Generate impact summary of changes."""
        original_lines = len(original_code.split('\n'))
        modified_lines = len(modified_code.split('\n'))
        
        return {
            'lines_changed': abs(modified_lines - original_lines),
            'change_percentage': round(abs(modified_lines - original_lines) / original_lines * 100, 2),
            'number_of_changes': len(changes_made),
            'original_lines': original_lines,
            'modified_lines': modified_lines
        }
    
    def get_stats(self) -> Dict:
        """Get AI engine statistics (NEW)."""
        return {
            'enabled': self.enabled,
            'api_calls': self.api_call_count,
            'fallback_mode': not self.enabled and self.optional
        }