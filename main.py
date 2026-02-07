#!/usr/bin/env python3
"""
Intelligent Release Management Scanner (IRMS)
Main orchestration script with batch processing and project-level ingestion

Enhanced with:
- Project-level ingestion (recursive scanning)
- Batch processing for scalability
- Optional AI with fallback
- Command-line arguments
"""
import sys
import argparse
import time
from pathlib import Path
from colorama import Fore, Style, init
from typing import Optional

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import (
    CODE_DIR, DOCS_DIR, MODIFIED_CODE_DIR, REPORTS_DIR,
    ENABLE_BATCH_PROCESSING, BATCH_SIZE, BATCH_DELAY,
    ENABLE_AI, AI_OPTIONAL,
    IGNORE_DIRECTORIES, MAX_FILE_SIZE
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


def parse_arguments():
    """Parse command-line arguments (NEW)."""
    parser = argparse.ArgumentParser(
        description='Intelligent Release Management Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  python main.py --project-path .
  
  # Scan with specific query
  python main.py --project-path /path/to/project --query "Add error handling"
  
  # Skip AI processing (static analysis only)
  python main.py --project-path . --no-ai
  
  # Non-interactive mode
  python main.py --project-path . --query "Improve code" --non-interactive
        """
    )
    
    parser.add_argument(
        '--project-path',
        type=str,
        default=None,
        help='Path to project root (enables recursive scanning)'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        default=None,
        help='Analysis query (skips interactive prompt)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI processing (static analysis only)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=BATCH_SIZE,
        help=f'Files per batch (default: {BATCH_SIZE})'
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Non-interactive mode (use with --query)'
    )
    
    return parser.parse_args()


def get_user_query(non_interactive: bool = False, default_query: Optional[str] = None) -> str:
    """
    Get natural language query from user.
    
    Args:
        non_interactive: Skip user input if True (NEW)
        default_query: Use this query in non-interactive mode (NEW)
    
    Returns:
        User's query string
    """
    if non_interactive and default_query:
        print_info(f"Using query: {default_query}")
        return default_query
    
    if non_interactive:
        query = "Analyze and improve code quality"
        print_info(f"Using default query: {query}")
        return query
    
    print(f"{Fore.CYAN}Please enter your change request:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}(What would you like to do with the code?){Style.RESET_ALL}")
    print(f"{Fore.GREEN}Example: 'Add error handling and improve code quality'{Style.RESET_ALL}\n")
    
    query = input(f"{Fore.CYAN}Your request: {Style.RESET_ALL}").strip()
    
    if not query:
        print_warning("No query provided. Using default: 'Analyze and improve code quality'")
        query = "Analyze and improve code quality"
    
    return query


def process_batch(
    files_batch: dict,
    analyzer: CodeAnalyzer,
    ai_engine: AIEngine,
    change_detector: ChangeDetector,
    risk_assessor: RiskAssessor,
    user_query: str,
    context_docs: str,
    ingestion: FileIngestion,
    batch_num: int,
    total_batches: int
) -> tuple:
    """
    Process a batch of files (NEW).
    
    Returns:
        Tuple of (analysis_results, ai_results, change_results, risk_assessments)
    """
    print_info(f"Processing batch {batch_num}/{total_batches} ({len(files_batch)} files)...")
    
    analysis_results = {}
    ai_results = {}
    change_results = {}
    risk_assessments = {}
    
    # Static Analysis
    for filename, source_code in files_batch.items():
        tree = ingestion.get_ast(filename)
        if tree is None:
            print_warning(f"Skipping {filename}: AST parsing failed")
            continue
        
        analysis = analyzer.analyze_file(filename, source_code, tree)
        analysis_results[filename] = analysis
    
    # AI Modification
    for filename, source_code in files_batch.items():
        if filename not in analysis_results:
            continue
        
        result = ai_engine.analyze_and_modify(
            source_code=source_code,
            filename=filename,
            user_query=user_query,
            static_analysis=analysis_results[filename],
            context_docs=context_docs
        )
        ai_results[filename] = result
        
        if result.get('fallback'):
            print_warning(f"AI unavailable for {filename}, using original code")
    
    # Change Detection
    for filename, source_code in files_batch.items():
        if filename not in ai_results:
            continue
        
        modified_code = ai_results[filename]['modified_code']
        changes = change_detector.detect_changes(filename, source_code, modified_code)
        change_results[filename] = changes
    
    # Risk Assessment
    for filename in analysis_results.keys():
        if filename not in change_results or filename not in ai_results:
            continue
        
        assessment = risk_assessor.assess_risk(
            filename=filename,
            original_analysis=analysis_results[filename],
            change_stats=change_results[filename]['statistics'],
            ai_changes=ai_results[filename]['changes_made']
        )
        risk_assessments[filename] = assessment
    
    print_success(f"Batch {batch_num} complete")
    
    return analysis_results, ai_results, change_results, risk_assessments


def main():
    """Main execution flow with batch processing."""
    args = parse_arguments()
    
    print_header()
    
    # Determine ingestion mode
    if args.project_path:
        project_path = Path(args.project_path).resolve()
        if not project_path.exists():
            print_error(f"Project path does not exist: {project_path}")
            return 1
        
        print_info(f"Project-level ingestion enabled: {project_path}")
        recursive = True
        code_dir = project_path
        docs_dir = project_path
    else:
        # Backward compatible mode
        if not CODE_DIR.exists() or not list(CODE_DIR.glob("*.py")):
            print_error(f"No Python files found in {CODE_DIR}")
            print_info(f"Tip: Use --project-path to scan entire projects")
            return 1
        recursive = False
        code_dir = CODE_DIR
        docs_dir = DOCS_DIR
    
    # PHASE 1: INGESTION
    print_section("PHASE 1: File Ingestion & Parsing")
    
    ingestion = FileIngestion(
        code_dir,
        docs_dir,
        project_root=code_dir if recursive else None,
        recursive=recursive,
        ignore_patterns=IGNORE_DIRECTORIES,
        max_file_size=MAX_FILE_SIZE
    )
    
    python_count = ingestion.ingest_python_files()
    print_success(f"Ingested {python_count} Python file(s)")
    
    if python_count == 0:
        print_error("No Python files to analyze")
        return 1
    
    doc_count = ingestion.ingest_documents()
    if doc_count > 0:
        print_success(f"Ingested {doc_count} supporting document(s)")
    
    # Get user query
    print_section("User Query Input")
    user_query = get_user_query(args.non_interactive, args.query)
    print_success(f"Query: '{user_query}'")
    
    # Combine documentation
    all_docs = ingestion.get_all_documents()
    context_docs = "\n\n".join([
        f"Document: {name}\n{content}"
        for name, content in all_docs.items()
    ])
    
    # Initialize modules
    analyzer = CodeAnalyzer()
    ai_engine = AIEngine(
        enabled=ENABLE_AI and not args.no_ai,
        optional=AI_OPTIONAL
    )
    change_detector = ChangeDetector()
    risk_assessor = RiskAssessor()
    
    if args.no_ai:
        print_warning("AI processing disabled (--no-ai flag)")
    
    # Prepare for batch processing
    all_files = ingestion.get_all_source_files()
    
    if ENABLE_BATCH_PROCESSING and len(all_files) > args.batch_size:
        print_section(f"Batch Processing ({len(all_files)} files, batch size: {args.batch_size})")
        
        # Split into batches
        file_items = list(all_files.items())
        batches = [
            dict(file_items[i:i + args.batch_size])
            for i in range(0, len(file_items), args.batch_size)
        ]
        
        # Aggregate results
        all_analysis = {}
        all_ai_results = {}
        all_changes = {}
        all_risks = {}
        
        for batch_num, batch in enumerate(batches, 1):
            analysis, ai_res, changes, risks = process_batch(
                batch, analyzer, ai_engine, change_detector, risk_assessor,
                user_query, context_docs, ingestion, batch_num, len(batches)
            )
            
            all_analysis.update(analysis)
            all_ai_results.update(ai_res)
            all_changes.update(changes)
            all_risks.update(risks)
            
            # Delay between batches
            if batch_num < len(batches):
                time.sleep(BATCH_DELAY)
            
            # Clear cache between batches
            ingestion.clear_cache()
        
        analysis_results = all_analysis
        ai_results = all_ai_results
        change_results = all_changes
        risk_assessments = all_risks
        
    else:
        # Single batch processing (original flow)
        print_section("Processing All Files")
        
        analysis_results, ai_results, change_results, risk_assessments = process_batch(
            all_files, analyzer, ai_engine, change_detector, risk_assessor,
            user_query, context_docs, ingestion, 1, 1
        )
    
    overall_risk = risk_assessor.get_overall_assessment()
    
    # PHASE 6: OUTPUT GENERATION
    print_section("Output Generation")
    
    # Write modified code files
    for filename, ai_result in ai_results.items():
        # Preserve directory structure
        output_path = MODIFIED_CODE_DIR / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ai_result['modified_code'])
        print_success(f"Modified code saved: {output_path}")
    
    # Generate comprehensive report
    report_gen = ReportGenerator(REPORTS_DIR)
    report_path = report_gen.generate_comprehensive_report(
        user_query=user_query,
        ingestion_summary=ingestion.get_summary(),
        analysis_results=analysis_results,
        ai_results=ai_results,
        change_results=change_results,
        risk_assessments=risk_assessments,
        overall_risk=overall_risk
    )
    
    print_success(f"Report generated: {report_path}")
    
    # FINAL SUMMARY
    print_section("Execution Complete")
    
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  Files Analyzed: {len(analysis_results)}")
    print(f"  Overall Decision: {overall_risk['overall_gate_decision']}")
    print(f"  Average Risk: {overall_risk['average_risk_score']:.2f}/100")
    print(f"  Report: {report_path}")
    
    # AI stats
    ai_stats = ai_engine.get_stats()
    if ai_stats['enabled']:
        print(f"  AI Calls: {ai_stats['api_calls']}")
    else:
        print(f"  AI: Disabled (fallback mode)")
    
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