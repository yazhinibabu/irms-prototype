#!/usr/bin/env python3
"""
IRMS Streamlit UI
Simple, professional interface for Intelligent Release Management Scanner
"""
import streamlit as st
import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import existing backend modules
from modules import (
    FileIngestion,
    CodeAnalyzer,
    AIEngine,
    ChangeDetector,
    RiskAssessor,
    ReportGenerator
)

# Configure page
st.set_page_config(
    page_title="IRMS - Intelligent Release Management Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_uploaded_files(uploaded_files, target_dir):
    """Save uploaded files to temporary directory."""
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = target_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(file_path)
    return saved_files


def run_irms_pipeline(code_dir, docs_dir, user_query):
    """Execute the IRMS pipeline and return results."""
    
    results = {
        'success': False,
        'ingestion': {},
        'analysis': {},
        'ai_results': {},
        'changes': {},
        'risk': {},
        'overall_risk': {},
        'report_path': None,
        'modified_files': {},
        'error': None
    }
    
    try:
        # Phase 1: Ingestion
        ingestion = FileIngestion(code_dir, docs_dir)
        python_count = ingestion.ingest_python_files()
        doc_count = ingestion.ingest_documents()
        
        if python_count == 0:
            results['error'] = "No Python files found to analyze"
            return results
        
        results['ingestion'] = {
            'python_files': list(ingestion.get_all_source_files().keys()),
            'documents': list(ingestion.get_all_documents().keys()),
            'summary': ingestion.get_summary()
        }
        
        # Combine documentation
        all_docs = ingestion.get_all_documents()
        context_docs = "\n\n".join([
            f"Document: {name}\n{content}"
            for name, content in all_docs.items()
        ])
        
        # Phase 2: Static Analysis
        analyzer = CodeAnalyzer()
        analysis_results = {}
        
        for filename, source_code in ingestion.get_all_source_files().items():
            tree = ingestion.get_ast(filename)
            if tree is None:
                continue
            analysis = analyzer.analyze_file(filename, source_code, tree)
            analysis_results[filename] = analysis
        
        results['analysis'] = analysis_results
        
        # Phase 3: AI Modification
        ai_engine = AIEngine()
        ai_results = {}
        
        for filename, source_code in ingestion.get_all_source_files().items():
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
            
            # Store modified code
            results['modified_files'][filename] = result['modified_code']
        
        results['ai_results'] = ai_results
        
        # Phase 4: Change Detection
        change_detector = ChangeDetector()
        change_results = {}
        
        for filename, source_code in ingestion.get_all_source_files().items():
            if filename not in ai_results:
                continue
            
            modified_code = ai_results[filename]['modified_code']
            changes = change_detector.detect_changes(filename, source_code, modified_code)
            change_results[filename] = changes
        
        results['changes'] = change_results
        
        # Phase 5: Risk Assessment
        risk_assessor = RiskAssessor()
        risk_assessments = {}
        
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
        
        results['risk'] = risk_assessments
        results['overall_risk'] = risk_assessor.get_overall_assessment()
        
        # Phase 6: Generate Report
        report_gen = ReportGenerator(Path(tempfile.gettempdir()))
        report_path = report_gen.generate_comprehensive_report(
            user_query=user_query,
            ingestion_summary=results['ingestion']['summary'],
            analysis_results=analysis_results,
            ai_results=ai_results,
            change_results=change_results,
            risk_assessments=risk_assessments,
            overall_risk=results['overall_risk']
        )
        
        results['report_path'] = report_path
        results['success'] = True
        
    except Exception as e:
        results['error'] = str(e)
        import traceback
        results['error_detail'] = traceback.format_exc()
    
    return results


def get_gate_color(decision):
    """Return color for gate decision."""
    colors = {
        'PASS': '#28a745',
        'WARN': '#ffc107',
        'BLOCK': '#dc3545'
    }
    return colors.get(decision, '#6c757d')


def create_risk_gauge(risk_score, gate_decision):
    """Create a gauge chart for risk score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score", 'font': {'size': 24}},
        delta={'reference': 30},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': get_gate_color(gate_decision)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#d4edda'},
                {'range': [30, 70], 'color': '#fff3cd'},
                {'range': [70, 100], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def markdown_to_pdf(markdown_path, pdf_path):
    """Convert markdown report to PDF using ReportLab."""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib.colors import HexColor
    import re
    
    try:
        # Read markdown
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for PDF elements
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        h1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            borderWidth=2,
            borderColor=HexColor('#3498db'),
            borderPadding=5
        )
        
        h2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10
        )
        
        normal_style = styles['Normal']
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontSize=9,
            leftIndent=20,
            backColor=HexColor('#f4f4f4')
        )
        
        # Parse markdown line by line
        lines = md_content.split('\n')
        in_code_block = False
        code_lines = []
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End code block
                    if code_lines:
                        code_text = '\n'.join(code_lines)
                        story.append(Preformatted(code_text, code_style))
                        story.append(Spacer(1, 0.2*inch))
                        code_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    in_code_block = True
                continue
            
            if in_code_block:
                code_lines.append(line)
                continue
            
            # Skip empty lines
            if not line.strip():
                story.append(Spacer(1, 0.1*inch))
                continue
            
            # Headers
            if line.startswith('# '):
                text = line[2:].strip()
                if 'Intelligent Release Management Scanner' in text:
                    story.append(Paragraph(text, title_style))
                else:
                    story.append(Paragraph(text, h1_style))
                story.append(Spacer(1, 0.1*inch))
            
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, h2_style))
                story.append(Spacer(1, 0.1*inch))
            
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
                story.append(Spacer(1, 0.05*inch))
            
            # Horizontal rules
            elif line.strip() == '---':
                story.append(Spacer(1, 0.2*inch))
            
            # Lists
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                text = line.strip()[2:]
                story.append(Paragraph(f"• {text}", normal_style))
            
            # Bold
            elif '**' in line:
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                story.append(Paragraph(text, normal_style))
            
            # Regular text
            else:
                story.append(Paragraph(line, normal_style))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

# ============================================================================
# MAIN UI
# ============================================================================

def main():
    # Header
    st.title("Intelligent Release Management Scanner (IRMS)")
    st.markdown("**AI-Powered Code Analysis & Risk Assessment**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("About IRMS")
        st.markdown("""
        IRMS analyzes your Python code using:
        - **Static Analysis** (complexity, issues)
        - **AI Enhancement** (via Google Gemini)
        - **Risk Assessment** (PASS/WARN/BLOCK)
        - **Change Tracking** (diffs & metrics)
        
        Perfect for release management and code reviews!
        """)
        
        st.markdown("---")
        st.markdown("**System Status**")
        st.success("Backend: Online")
        st.info("AI Model: Gemini 2.5 Flash")
    
    # ========================================================================
    # INPUT SECTION
    # ========================================================================
    
    st.header("Step 1: Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Python Source Files *")
        uploaded_py_files = st.file_uploader(
            "Upload Python files (.py)",
            type=['py'],
            accept_multiple_files=True,
            help="Upload one or more Python files to analyze"
        )
    
    with col2:
        st.subheader("Documentation (Optional)")
        uploaded_doc_files = st.file_uploader(
            "Upload documentation files",
            type=['txt', 'pdf', 'md'],
            accept_multiple_files=True,
            help="Upload requirements, specs, or other documentation"
        )
    
    st.markdown("---")
    
    st.header("Step 2: Describe Changes")
    
    user_query = st.text_area(
        "What improvements would you like AI to make?",
        value="Add comprehensive error handling, type hints, docstrings, and logging to all functions",
        height=100,
        help="Describe what you want the AI to improve in natural language"
    )
    
    st.markdown("---")
    
    # ========================================================================
    # RUN ANALYSIS
    # ========================================================================
    
    st.header("Step 3: Run Analysis")
    
    run_button = st.button(
        "Run IRMS Analysis",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_py_files
    )
    
    if not uploaded_py_files and not run_button:
        st.info("Upload Python files to begin")
        return
    
    # ========================================================================
    # PROCESSING & RESULTS
    # ========================================================================
    
    if run_button:
        if not uploaded_py_files:
            st.error("Please upload at least one Python file")
            return
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            code_dir = temp_path / "code"
            docs_dir = temp_path / "docs"
            code_dir.mkdir()
            docs_dir.mkdir()
            
            # Save uploaded files
            with st.spinner("Uploading files..."):
                save_uploaded_files(uploaded_py_files, code_dir)
                if uploaded_doc_files:
                    save_uploaded_files(uploaded_doc_files, docs_dir)
            
            # Run pipeline
            with st.spinner("Running IRMS pipeline... This may take a minute."):
                results = run_irms_pipeline(code_dir, docs_dir, user_query)
            
            # Store in session state
            st.session_state['results'] = results
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    if 'results' in st.session_state:
        results = st.session_state['results']
        
        if not results['success']:
            st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            if results.get('error_detail'):
                with st.expander("Error Details"):
                    st.code(results['error_detail'])
            return
        
        st.success("Analysis complete!")
        st.markdown("---")
        
        # ====================================================================
        # OVERALL RESULTS
        # ====================================================================
        
        st.header("Overall Results")
        
        overall = results['overall_risk']
        gate_decision = overall.get('overall_gate_decision', 'PENDING')
        risk_score = overall.get('average_risk_score', 0)
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gate Decision",
                gate_decision,
                delta=None,
                delta_color="normal"
            )
            color = get_gate_color(gate_decision)
            st.markdown(
                f'<div style="background-color: {color}; color: white; '
                f'padding: 10px; border-radius: 5px; text-align: center; '
                f'font-weight: bold; margin-top: -10px;">{gate_decision}</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.metric("Risk Score", f"{risk_score:.1f}/100")
        
        with col3:
            st.metric("Files Analyzed", overall.get('files_assessed', 0))
        
        with col4:
            gate_counts = overall.get('gate_counts', {})
            st.metric("Files Passed", gate_counts.get('PASS', 0))
        
        # Risk gauge
        st.plotly_chart(
            create_risk_gauge(risk_score, gate_decision),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # ====================================================================
        # CHANGE SUMMARY
        # ====================================================================
        
        st.header("Change Summary")
        
        total_added = 0
        total_deleted = 0
        total_modified = 0
        
        for change in results['changes'].values():
            stats = change['statistics']
            total_added += stats.get('lines_added', 0)
            total_deleted += stats.get('lines_deleted', 0)
            total_modified += stats.get('lines_modified', 0)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Lines Added", f"+{total_added}", delta_color="normal")
        col2.metric("Lines Deleted", f"-{total_deleted}", delta_color="inverse")
        col3.metric("Lines Modified", f"~{total_modified}", delta_color="off")
        
        st.markdown("---")
        
        # ====================================================================
        # FILE DETAILS
        # ====================================================================
        
        st.header("File-by-File Details")
        
        for filename, risk_assessment in results['risk'].items():
            with st.expander(f" {filename} - {risk_assessment['gate_decision']} (Risk: {risk_assessment['risk_score']:.1f})"):
                
                # Analysis
                analysis = results['analysis'].get(filename, {})
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Code Analysis")
                    metrics = analysis.get('metrics', {})
                    complexity = analysis.get('complexity', {})
                    st.write(f"**Complexity:** {complexity.get('average', 0):.1f}")
                    st.write(f"**Maintainability:** {metrics.get('maintainability_index', 0):.1f}")
                    st.write(f"**Issues Found:** {len(analysis.get('issues', []))}")
                
                with col2:
                    st.subheader("Changes Applied")
                    changes = results['changes'].get(filename, {}).get('statistics', {})
                    st.write(f"**Added:** +{changes.get('lines_added', 0)}")
                    st.write(f"**Deleted:** -{changes.get('lines_deleted', 0)}")
                    st.write(f"**Modified:** ~{changes.get('lines_modified', 0)}")
                
                # AI Changes
                ai_result = results['ai_results'].get(filename, {})
                if ai_result.get('changes_made'):
                    st.subheader("AI-Suggested Changes")
                    for i, change in enumerate(ai_result['changes_made'], 1):
                        st.write(f"- {change}")
                
                # Issues
                issues = analysis.get('issues', [])
                if issues:
                    st.subheader("Issues Detected")
                    for issue in issues[:5]:
                        severity_color = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢',
                            'info': '🔵'
                        }.get(issue.get('severity', 'info'), '⚪')
                        st.write(f"{severity_color} Line {issue['line']}: {issue['message']}")
        
        st.markdown("---")
        
        # ====================================================================
        # DOWNLOADS
        # ====================================================================
        
        st.header(" Downloads")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Modified Code")
            for filename, modified_code in results['modified_files'].items():
                st.download_button(
                    label=f"📄 Download {filename}",
                    data=modified_code,
                    file_name=f"modified_{filename}",
                    mime="text/x-python"
                )
        
        with col2:
            st.subheader("Report")
            
            # Markdown report
            if results.get('report_path'):
                with open(results['report_path'], 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                st.download_button(
                    label=" Download Report (Markdown)",
                    data=report_content,
                    file_name=f"IRMS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # PDF report
                pdf_path = Path(tempfile.gettempdir()) / f"IRMS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                if st.button(" Generate PDF Report"):
                    with st.spinner("Generating PDF..."):
                        if markdown_to_pdf(results['report_path'], str(pdf_path)):
                            with open(pdf_path, 'rb') as f:
                                st.download_button(
                                    label=" Download Report (PDF)",
                                    data=f.read(),
                                    file_name=pdf_path.name,
                                    mime="application/pdf"
                                )
                            st.success("PDF generated successfully!")


if __name__ == "__main__":
    main()