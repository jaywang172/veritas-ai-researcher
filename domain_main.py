#!/usr/bin/env python3
"""
Domain-Adaptive Research Main - Linux Philosophy Implementation
Configurable research pipeline that adapts to different domains.

Usage: python domain_main.py [domain]
Domains: business, academic, technical, scientific, general
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

from workflows.domain_adaptive_workflow import (
    create_domain_adaptive_workflow, 
    ResearchDomain, 
    DOMAIN_CONFIGS,
    WorkflowError
)

load_dotenv()


def print_header():
    print("=" * 60)
    print("Domain-Adaptive Research Pipeline".center(60))
    print("Linux Philosophy: Configurable, Composable, Reliable".center(60))
    print("=" * 60 + "\n")


def print_domain_options():
    print("Available research domains:")
    print("-" * 40)
    for domain, config in DOMAIN_CONFIGS.items():
        print(f"  {domain.value:<12} - {config.writing_style}")
        focus_preview = ", ".join(config.data_analysis_focus[:3])
        print(f"              Focus: {focus_preview}...")
    print("-" * 40 + "\n")


def select_domain() -> ResearchDomain:
    """Interactive domain selection with auto-detection option."""
    print_domain_options()
    
    choice = input("Select domain (or 'auto' for detection): ").strip().lower()
    
    if choice == 'auto' or choice == '':
        return None  # Will trigger auto-detection
    
    # Map user input to domain
    domain_map = {
        'business': ResearchDomain.BUSINESS,
        'b': ResearchDomain.BUSINESS,
        'academic': ResearchDomain.ACADEMIC,
        'a': ResearchDomain.ACADEMIC,
        'technical': ResearchDomain.TECHNICAL,
        't': ResearchDomain.TECHNICAL,
        'scientific': ResearchDomain.SCIENTIFIC,
        's': ResearchDomain.SCIENTIFIC,
        'general': ResearchDomain.GENERAL,
        'g': ResearchDomain.GENERAL
    }
    
    domain = domain_map.get(choice)
    if domain:
        print(f"Selected domain: {domain.value}")
        return domain
    else:
        print("Invalid selection, using auto-detection")
        return None


def main():
    print_header()
    
    # Domain selection
    if len(sys.argv) > 1:
        # Command line domain specification
        domain_arg = sys.argv[1].lower()
        domain_map = {
            'business': ResearchDomain.BUSINESS,
            'academic': ResearchDomain.ACADEMIC,
            'technical': ResearchDomain.TECHNICAL,
            'scientific': ResearchDomain.SCIENTIFIC,
            'general': ResearchDomain.GENERAL
        }
        domain = domain_map.get(domain_arg)
        if not domain:
            print(f"ERROR: Unknown domain '{domain_arg}'")
            print("Valid domains: business, academic, technical, scientific, general")
            sys.exit(1)
        print(f"Command line domain: {domain.value}")
    else:
        # Interactive selection
        domain = select_domain()
    
    # Research objective
    goal = input("Research objective: ").strip()
    if not goal:
        print("ERROR: Research objective is required")
        sys.exit(1)
    
    # Optional data file
    data_file = input("Data file path (optional): ").strip()
    if data_file and not Path(data_file).exists():
        print(f"WARNING: File '{data_file}' not found")
        use_anyway = input("Continue without data file? (y/N): ").strip().lower()
        if use_anyway != 'y':
            sys.exit(1)
        data_file = None
    
    print("\n" + "=" * 60)
    print("PIPELINE CONFIGURATION")
    print("=" * 60)
    print(f"Research goal: {goal}")
    print(f"Data source: {data_file if data_file else 'Literature only'}")
    print(f"Domain: {domain.value if domain else 'Auto-detect'}")
    
    if domain:
        config = DOMAIN_CONFIGS[domain]
        print(f"Focus areas: {', '.join(config.data_analysis_focus[:3])}...")
        print(f"Writing style: {config.writing_style}")
        print(f"Output format: {config.output_format}")
    
    print("=" * 60 + "\n")
    
    try:
        # Create and run workflow
        workflow = create_domain_adaptive_workflow(domain)
        document = workflow.run(goal, data_file)
        result = document.get_content()
        
        # Success report
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED")
        print("=" * 60)
        print(f"Final domain: {workflow.domain.value}")
        print(f"Content length: {len(result)} characters")
        print(f"Word count: ~{len(result.split())} words")
        print(f"Results directory: {workflow.domain_dir}")
        
        # List generated files
        artifacts = list(workflow.domain_dir.glob("*"))
        if artifacts:
            print(f"\nGenerated files:")
            for artifact in sorted(artifacts):
                if artifact.is_file():
                    size = artifact.stat().st_size
                    print(f"  - {artifact.name} ({size:,} bytes)")
        
        print(f"\nSuccess: Domain-adaptive research completed")
        
    except WorkflowError as e:
        print("\n" + "=" * 60)
        print("PIPELINE FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  - Check data file format and accessibility")
        print("  - Verify API keys and connectivity")  
        print("  - Try a different domain configuration")
        print("  - Review research objective clarity")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
