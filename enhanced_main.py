#!/usr/bin/env python3
"""
Veritas Enhanced Main - Academic rigor meets practical delivery
Multi-round reviews + comprehensive analysis + actionable insights.

Usage: python enhanced_main.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from workflows.enhanced_workflow import create_enhanced_workflow, WorkflowError
from datetime import datetime

load_dotenv()


def print_header():
    print("=" * 70)
    print("Veritas Enhanced - Academic Rigor + Business Insights".center(70))
    print("Multi-Round Reviews - Comprehensive Analysis - Actionable Results".center(70))
    print("=" * 70 + "\n")


def save_result(content: str, goal: str, session_dir: Path = None) -> str:
    """Save enhanced research result with executive summary."""
    # Create results directory structure
    if session_dir is None:
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = results_dir / f"enhanced_research_{timestamp}"
        session_dir.mkdir(exist_ok=True)
    
    # Create safe filename
    safe_goal = "".join(c for c in goal if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_goal = safe_goal.replace(' ', '_')[:30]
    
    filename = session_dir / f"ENHANCED_RESEARCH_{safe_goal}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Enhanced Research Report: {goal}\n")
            f.write(f"# Generated: {session_dir}\n")
            f.write(f"# Process: Multi-round academic review with business insights\n")
            f.write("=" * 70 + "\n\n")
            f.write(content)
        
        print(f"Report saved: {filename}")
        return str(filename)
    except Exception as e:
        print(f"WARNING: Could not save to {filename}: {e}")
        return None


def print_process_overview():
    print("Enhanced Research Process Overview:")
    print("-" * 50)
    print("   Phase 1: Literature Research")
    print("     - Literature research (global sources)")
    print("     - Comprehensive data analysis (if provided)")
    print("     - Business intelligence & insights")
    print("   Phase 2: Analysis & Synthesis")
    print("     - Synthesis of findings")
    print("     - Strategic outline creation")
    print("   Phase 3: Multi-Round Review")
    print("     - Initial draft creation")
    print("     - Review Cycle 1: Structure & content")
    print("     - Review Cycle 2: Academic rigor & polish")
    print("   Phase 4: Professional Finalization")
    print("     - Professional editing")
    print("     - Citation formatting")
    print("     - Executive summary generation")
    print("-" * 50 + "\n")


def main():
    print_header()
    
    goal = input("Research objective: ").strip()
    if not goal:
        print("ERROR: Research objective is required")
        sys.exit(1)
    
    # Optional data file
    data_file = input("Data file for analysis (optional, press Enter to skip): ").strip()
    if data_file and not Path(data_file).exists():
        print(f"WARNING: File '{data_file}' not found, proceeding with literature-only analysis")
        data_file = None
    
    print_process_overview()
    
    print(f"Research Goal: {goal}")
    print(f"Data Source: {data_file if data_file else 'Literature sources only'}")
    print(f"Expected deliverables: Comprehensive report + visualizations + insights")
    print("=" * 70)
    
    try:
        # Create and run the enhanced workflow
        workflow = create_enhanced_workflow()
        document = workflow.run(goal, data_file)
        result = document.get_content()
        
        # Save result to the session directory
        filename = save_result(result, goal, workflow.session_dir)
        
        # Display completion metrics
        print("=" * 70)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        print(f"Content metrics:")
        print(f"   - Total length: {len(result)} characters")
        print(f"   - Word count: ~{len(result.split())} words")
        print(f"   - Estimated reading time: ~{len(result.split())//200} minutes")
        
        print(f"\nGenerated artifacts in {workflow.session_dir}:")
        # Check for generated files in session directory
        artifacts = []
        if workflow.session_dir.exists():
            artifacts = list(workflow.session_dir.glob("*"))
        
        if artifacts:
            for artifact in sorted(artifacts):
                file_size = artifact.stat().st_size if artifact.is_file() else 0
                size_str = f"({file_size:,} bytes)" if file_size > 0 else ""
                print(f"   - {artifact.name} {size_str}")
        else:
            print("   - Main research report")
            
        print(f"\nResults directory: {workflow.session_dir}")
        
        print(f"\nKey deliverables for management:")
        print(f"   - Executive summary with actionable insights")
        print(f"   - Data-driven analysis with visualizations")
        print(f"   - Strategic recommendations")
        print(f"   - Academic-quality citations and references")
        print(f"   - Multi-round peer review validation")
        
        print(f"\nSuccess! Research completed and saved to: {filename}")
        
    except WorkflowError as e:
        print("=" * 70)
        print("WORKFLOW TROUBLESHOOTING")
        print("=" * 70)
        print("Common issues and solutions:")
        print("  - Data quality or accessibility problems")
        print("  - API rate limits or connectivity issues")  
        print("  - Complex research objectives requiring human input")
        print(f"\nSpecific error: {e}")
        print("\nFor support, check the workflow logs above.")
        sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: Unexpected failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
