#!/usr/bin/env python3
"""
IRMS Demo Script

This script demonstrates the IRMS system with predefined inputs
to show its capabilities without requiring user interaction.
"""
import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import CODE_DIR, DOCS_DIR, MODIFIED_CODE_DIR, REPORTS_DIR
from modules import (
    FileIngestion,
    CodeAnalyzer,
    AIEngine,
    ChangeDetector,
    RiskAssessor,
    ReportGenerator
)


def demo_run():
    """Run IRMS demonstration."""
    print("="*80)
    print("IRMS DEMONSTRATION".center(80))
    print("="*80)
    print()
    
    # Predefined query
    user_query = "Add comprehensive error handling, type hints, docstrings, and logging to all functions"
    
    print(f"Demo Query: '{user_query}'")
    print()
    
    # Check inputs
    py_files = list(CODE_DIR.glob("*.py"))
    if not py_files:
        print("ERROR: No sample files found!")
        print(f"Please ensure sample files exist in {CODE_DIR}")
        return 1
    
    print(f"Found {len(py_files)} Python file(s) to analyze")
    print()
    
    # Phase 1: Ingestion
    print("[1/6] Ingesting files...")
    ingestion = FileIngestion(CODE_DIR, DOCS_DIR)
    python_count = ingestion.ingest_python_files()
    doc_count = ingestion.ingest_documents()
    print(f"  ✓ {python_count} Python files, {doc_count} documents")
    
    # Combine documentation
    all_docs = ingestion.get_all_documents()
    context_docs = "\n\n".join([f"Document: {name}\n{content}" for name, content in all_docs.items()])
    
    # Phase 2: Static Analysis
    print("[2/6] Performing static analysis...")
    analyzer = CodeAnalyzer()
    analysis_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        tree = ingestion.get_ast(filename)
        if tree is None:
            print(f"  ✗ Skipping {filename}: Failed to parse AST")
            continue
        analysis = analyzer.analyze_file(filename, source_code, tree)
        analysis_results[filename] = analysis
        print(f"  ✓ {filename}: Complexity={analysis['complexity']['average']:.1f}, Issues={len(analysis['issues'])}")
    
    # Phase 3: AI Modification
    print("[3/6] Applying AI-powered modifications...")
    ai_engine = AIEngine()
    ai_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        print(f"  Processing {filename}...")
        result = ai_engine.analyze_and_modify(
            source_code=source_code,
            filename=filename,
            user_query=user_query,
            static_analysis=analysis_results[filename],
            context_docs=context_docs
        )
        ai_results[filename] = result
        print(f"  ✓ {len(result['changes_made'])} changes applied")
    
    # Phase 4: Change Detection
    print("[4/6] Detecting changes...")
    change_detector = ChangeDetector()
    change_results = {}
    
    for filename, source_code in ingestion.get_all_source_files().items():
        modified_code = ai_results[filename]['modified_code']
        changes = change_detector.detect_changes(filename, source_code, modified_code)
        change_results[filename] = changes
        stats = changes['statistics']
        print(f"  ✓ {filename}: +{stats['lines_added']} -{stats['lines_deleted']} ~{stats['lines_modified']}")
    
    # Phase 5: Risk Assessment
    print("[5/6] Assessing risks...")
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
        print(f"  ✓ {filename}: {assessment['gate_decision']} (Risk: {assessment['risk_score']:.1f}/100)")
    
    overall_risk = risk_assessor.get_overall_assessment()
    
    # Phase 6: Output Generation
    print("[6/6] Generating outputs...")
    
    # Save modified files
    for filename, ai_result in ai_results.items():
        output_path = MODIFIED_CODE_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ai_result['modified_code'])
    
    # Generate report
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
    
    print(f"  ✓ Report: {report_path}")
    print(f"  ✓ Modified code: {MODIFIED_CODE_DIR}")
    
    # Summary
    print()
    print("="*80)
    print("DEMO COMPLETE".center(80))
    print("="*80)
    print()
    print(f"Overall Gate Decision: {overall_risk['overall_gate_decision']}")
    print(f"Average Risk Score: {overall_risk['average_risk_score']:.2f}/100")
    print(f"Files Analyzed: {len(analysis_results)}")
    print()
    print("Check the outputs directory for results!")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = demo_run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
