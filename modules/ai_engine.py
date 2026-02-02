"""
AI-assisted code analysis and modification engine using Google Gemini
"""
from typing import Dict, List, Optional, Any
import os
from pathlib import Path
from config.settings import AI_MODEL, MAX_TOKENS, TEMPERATURE

# Import Google Generative AI
try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    raise ImportError(
        "google-generativeai not installed. Run: pip install google-generativeai"
    )

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
    
    def __init__(self):
        """Initialize the AI engine with Gemini API."""
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set. "
                "Get your free API key at https://makersuite.google.com/app/apikey"
            )
        
        genai.configure(api_key=api_key)  # type: ignore
        self.model = genai.GenerativeModel(AI_MODEL)  # type: ignore
        self.conversation_history: List[Dict] = []
    
    def analyze_and_modify(
        self,
        source_code: str,
        filename: str,
        user_query: str,
        static_analysis: Dict,
        context_docs: str = ""
    ) -> Dict[str, Any]:
        """
        Use AI to analyze code and generate modifications based on user query.
        
        Args:
            source_code: Original Python source code
            filename: Name of the file
            user_query: User's natural language request
            static_analysis: Results from static analysis
            context_docs: Supporting documentation context
            
        Returns:
            Dictionary with modified code and explanation
        """
        prompt = self._build_analysis_prompt(
            source_code, filename, user_query, static_analysis, context_docs
        )
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)  # type: ignore
            response_text = response.text
            
            if not response_text:
                raise ValueError("Received empty response from AI model.")
            
            result = self._parse_ai_response(response_text, source_code)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                'modified_code': source_code,
                'changes_made': [],
                'explanation': f"Error during AI analysis: {str(e)}",
                'success': False
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
            'success': True
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