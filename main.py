#!/usr/bin/env python3
"""
Intelligent Release Management Scanner (IRMS)
Main orchestration script

This script ties together all modules to provide end-to-end
code analysis, modification, and release management.
"""
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import (
    CODE_DIR, DOCS_DIR, MODIFIED_CODE_DIR, REPORTS_DIR
)
from modules import (
    FileIngestion,
    CodeAnalyzer,
    AIEngine,
    ChangeDetector,
    RiskAssessor,
    ReportGenerator
)


def print_header():
    """Print IRMS header."""
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{'Intelligent Release Management Scanner (IRMS)':^80}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


def print_section(title: str):
    """Print section header."""
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"{Fore.YELLOW}{title:^80}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def get_user_query() -> str:
    """
    Get natural language query from user.
    
    Returns:
        User's query string
    """
    print(f"{Fore.CYAN}Please enter your change request:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}(What would you like to do with the code?){Style.RESET_ALL}")
    print(f"{Fore.GREEN}Example: 'Add error handling and improve code quality'{Style.RESET_ALL}\n")
    
    query = input(f"{Fore.CYAN}Your request: {Style.RESET_ALL}").strip()
    
    if not query:
        print_warning("No query provided. Using default: 'Analyze and improve code quality'")
        query = "Analyze and improve code quality"
    
    return query


def main():
    """Main execution flow."""
    print_header()
    
    # Check that input directories exist and have files
    if not CODE_DIR.exists() or not list(CODE_DIR.glob("*.py")):
        print_error(f"No Python files found in {CODE_DIR}")
        print_info(f"Please place Python source files in: {CODE_DIR}")
        return 1
    
    # PHASE 1: INGESTION
    print_section("PHASE 1: File Ingestion & Parsing")
    
    ingestion = FileIngestion(CODE_DIR, DOCS_DIR)
    
    python_count = ingestion.ingest_python_files()
    print_success(f"Ingested {python_count} Python file(s)")
    
    doc_count = ingestion.ingest_documents()
    if doc_count > 0:
        print_success(f"Ingested {doc_count} supporting document(s)")
    else:
        print_info("No supporting documents found")
    
    ingestion_summary = ingestion.get_summary()
    
    # Get user query
    print_section("User Query Input")
    user_query = get_user_query()
    print_success(f"Query received: '{user_query}'")
    
    # Combine all documentation for context
    all_docs = ingestion.get_all_documents()
    context_docs = "\n\n".join([
        f"Document: {name}\n{content}"
        for name, content in all_docs.items()
    ])
    
    # PHASE 2: STATIC ANALYSIS
    print_section("PHASE 2: Static Code Analysis")
    
    analyzer = CodeAnalyzer()
    analysis_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        print_info(f"Analyzing {filename}...")
        tree = ingestion.get_ast(filename)
        analysis = analyzer.analyze_file(filename, source_code, tree)
        analysis_results[filename] = analysis
        
        print(f"  - Complexity: {analysis['complexity']['average']:.2f}")
        print(f"  - Issues: {len(analysis['issues'])}")
    
    print_success(f"Static analysis complete for {len(analysis_results)} file(s)")
    
    # PHASE 3: AI-ASSISTED MODIFICATION
    print_section("PHASE 3: AI-Assisted Code Modification")
    
    ai_engine = AIEngine()
    ai_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        print_info(f"AI analyzing {filename}...")
        
        result = ai_engine.analyze_and_modify(
            source_code=source_code,
            filename=filename,
            user_query=user_query,
            static_analysis=analysis_results[filename],
            context_docs=context_docs
        )
        
        ai_results[filename] = result
        
        if result['success']:
            print_success(f"AI modifications generated for {filename}")
            print(f"  - Changes: {len(result['changes_made'])}")
        else:
            print_warning(f"AI analysis had issues for {filename}")
    
    # PHASE 4: CHANGE DETECTION
    print_section("PHASE 4: Change Detection & Analysis")
    
    change_detector = ChangeDetector()
    change_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        modified_code = ai_results[filename]['modified_code']
        
        changes = change_detector.detect_changes(filename, source_code, modified_code)
        change_results[filename] = changes
        
        stats = changes['statistics']
        print_info(f"{filename}:")
        print(f"  + {stats['lines_added']} additions")
        print(f"  - {stats['lines_deleted']} deletions")
        print(f"  ~ {stats['lines_modified']} modifications")
    
    # PHASE 5: RISK ASSESSMENT
    print_section("PHASE 5: Risk Assessment & Gate Decision")
    
    risk_assessor = RiskAssessor()
    risk_assessments = {}
    
    for filename in analysis_results.keys():
        assessment = risk_assessor.assess_risk(
            filename=filename,
            original_analysis=analysis_results[filename],
            change_stats=change_results[filename]['statistics'],
            ai_changes=ai_results[filename]['changes_made']
        )
        
        risk_assessments[filename] = assessment
        
        # Color-code gate decision
        decision = assessment['gate_decision']
        if decision == 'PASS':
            print_success(f"{filename}: {decision} (Risk: {assessment['risk_score']:.2f})")
        elif decision == 'WARN':
            print_warning(f"{filename}: {decision} (Risk: {assessment['risk_score']:.2f})")
        else:
            print_error(f"{filename}: {decision} (Risk: {assessment['risk_score']:.2f})")
    
    overall_risk = risk_assessor.get_overall_assessment()
    
    print(f"\n{Fore.CYAN}Overall Assessment:{Style.RESET_ALL}")
    print(f"  Average Risk Score: {overall_risk['average_risk_score']:.2f}/100")
    print(f"  Gate Decision: {overall_risk['overall_gate_decision']}")
    
    # PHASE 6: OUTPUT GENERATION
    print_section("PHASE 6: Output Generation")
    
    # Write modified code files
    for filename, ai_result in ai_results.items():
        output_path = MODIFIED_CODE_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ai_result['modified_code'])
        print_success(f"Modified code saved: {output_path}")
    
    # Generate comprehensive report
    report_gen = ReportGenerator(REPORTS_DIR)
    report_path = report_gen.generate_comprehensive_report(
        user_query=user_query,
        ingestion_summary=ingestion_summary,
        analysis_results=analysis_results,
        ai_results=ai_results,
        change_results=change_results,
        risk_assessments=risk_assessments,
        overall_risk=overall_risk
    )
    
    print_success(f"Comprehensive report generated: {report_path}")
    
    # FINAL SUMMARY
    print_section("Execution Complete")
    
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  Files Analyzed: {len(analysis_results)}")
    print(f"  Files Modified: {len(ai_results)}")
    print(f"  Overall Decision: {overall_risk['overall_gate_decision']}")
    print(f"  Report: {report_path}")
    print(f"  Modified Code: {MODIFIED_CODE_DIR}")
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}{'IRMS Analysis Complete!':^80}")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
