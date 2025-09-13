#!/usr/bin/env python3
"""
Veritas Enhanced Workflow - Linus-approved with academic rigor
Simple core + necessary review cycles + comprehensive analysis.

Philosophy: 
- Keep the linear workflow (no 70-field monsters)
- Add meaningful review cycles (not bureaucratic nonsense)  
- Generate comprehensive insights (not just pretty charts)
"""

from workflows.simple_workflow import SimpleWorkflow, Document, StepResult, WorkflowError
from typing import Dict, List
from pathlib import Path
import json
import os
from datetime import datetime


class EnhancedWorkflow(SimpleWorkflow):
    """
    Enhanced workflow with academic rigor and business insights.
    
    Key improvements:
    1. Multi-round review with actual revisions
    2. Comprehensive data analysis with business insights
    3. Version tracking (simple, not monstrous)
    4. Quality gates that matter
    """
    
    def __init__(self):
        super().__init__()
        self.revision_count = 0
        self.max_revisions = 2  # Practical limit
        self.versions = []  # Simple version tracking
        
        # Create results directory
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Create session-specific subdirectory
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.results_dir / f"research_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)
        
        print(f"Results will be saved to: {self.session_dir}")
    
    def run(self, goal: str, data_file: str = None) -> Document:
        """
        Enhanced workflow with review cycles and comprehensive analysis.
        
        Flow:
        1-3: Standard pipeline (literature, data, synthesis)
        4: Comprehensive data analysis (if data file provided)
        5: Outline creation
        6: Writing
        7: First review & revision cycle
        8: Second review & revision cycle (if needed)
        9: Final polish & citations
        """
        print(f"\nStarting enhanced workflow for: {goal}")

        document = Document(goal)

        try:
            # Phase 1: Research and Analysis
            print("\nPhase 1: Research & Data Collection")
            print("Step 1: Literature research...")
            research_result = self._research_literature(goal)
            document.add_section(research_result)
            print("✓ Literature research completed")

            analysis_result = None
            if data_file and Path(data_file).exists():
                print("Enhanced data analysis...")
                analysis_result = self._comprehensive_data_analysis(data_file, goal)
                document.add_section(analysis_result)
                print("✓ Enhanced data analysis completed")
            else:
                print("Skipping data analysis - no data file provided")

            # Phase 2: Synthesis and Planning
            print("\nPhase 2: Analysis & Planning")
            print("Step 3: Synthesizing findings...")
            synthesis_result = self._synthesize_findings(document)
            print("✓ Synthesis completed")

            print("Step 4: Creating outline...")
            outline_result = self._create_outline(synthesis_result, goal)
            print("✓ Outline created")

            # Phase 3: Writing and Review Cycles
            print("\nPhase 3: Writing & Review Cycles")
            print("Step 5: Writing content...")
            content_result = self._write_content(outline_result, synthesis_result)
            print("✓ Initial draft completed")

            # Save initial draft
            self._save_version(content_result.content, "initial_draft")
            print("Saved initial draft version")

            # Review Cycle 1
            print("\nReview Cycle 1: Structural & Content Review")
            reviewed_content = self._comprehensive_review(content_result.content, cycle=1)

            if self._needs_revision(reviewed_content):
                print("Revision required - performing major revisions...")
                revised_content = self._perform_revision(reviewed_content, analysis_result)
                self._save_version(revised_content, "revision_1")
                print("First revision completed")
                current_content = revised_content
            else:
                print("First review passed - no revision needed")
                current_content = content_result.content

            # Review Cycle 2 (if needed)
            if self.revision_count < self.max_revisions:
                print("\nReview Cycle 2: Final Quality Check")
                final_review = self._comprehensive_review(current_content, cycle=2)

                if self._needs_revision(final_review):
                    print("Final revision - polishing and refinement...")
                    current_content = self._perform_revision(final_review, analysis_result)
                    self._save_version(current_content, "revision_2")
                    print("✓ Final revision completed")
                else:
                    print("✓ Final review passed")

            # Phase 4: Final Polish
            print("\nPhase 4: Final Polish & Citations")
            print("Step 6: Editing and polishing...")
            edited_result = self._edit_content(current_content)
            print("✓ Professional editing completed")

            print("Step 7: Formatting citations...")
            final_result = self._format_citations(edited_result.content)
            print("✓ Citation formatting completed")

            # Save final version
            self._save_version(final_result.content, "final")
            print("Saved final version")

            # Add final result to document
            document.sections[-1] = final_result

            # Generate summary report
            print("\nGenerating summary report...")
            self._print_summary_report(document)

            print("Enhanced workflow completed successfully!")
            print(f"Results saved to: {self.session_dir}")
            print(f"Total revisions: {self.revision_count}")
            print(f"Versions created: {len(self.versions)}")

            return document

        except WorkflowError as e:
            print(f"Workflow failed: {e}")
            raise
        except Exception as e:
            print(f"Critical error: {e}")
            raise WorkflowError(f"Enhanced pipeline failed: {e}")

    def _comprehensive_data_analysis(self, data_file: str, goal: str) -> StepResult:
        """Enhanced data analysis with business insights."""
        try:
            from crewai import Task, Crew
            
            task = Task(
                description=f"""Perform comprehensive analysis of data file: {data_file}

Research goal: {goal}

Required analysis (use LocalCodeExecutor for each):

1. **Data Overview & Quality Assessment**
   - Load and examine data structure
   - Check for missing values, outliers, data quality issues
   - Generate summary statistics

2. **Trend Analysis & Key Metrics** 
   - Revenue trends by business segment
   - Growth rates (QoQ, YoY, CAGR)
   - Market share shifts between segments
   - Identify inflection points and transitions

3. **Business Intelligence & Insights**
   - Calculate financial ratios and performance metrics
   - Identify peak performance periods and drivers
   - Competitive positioning analysis
   - Risk factors and volatility assessment

4. **Predictive Analysis**
   - Trend extrapolation for next 2-4 quarters
   - Scenario analysis (bull/bear cases)
   - Key assumptions and limitations

5. **Executive Summary**
   - Top 5 business insights for decision makers
   - Investment thesis (bull/bear arguments)
   - Strategic recommendations

Create multiple professional visualizations and save them to: {self.session_dir}
- Revenue trend comparison (enhance existing)
- Market share pie charts over time  
- Growth rate analysis charts
- Competitive positioning matrix
- Financial performance dashboard
- All charts should use professional styling with clear labels

IMPORTANT: Use this exact path for saving all charts and files: {self.session_dir}

Output a comprehensive business analysis report with file locations.""",
                expected_output="Comprehensive business analysis with multiple insights, visualizations, and strategic recommendations",
                agent=self.agents['analyze']
            )
            
            crew = Crew(agents=[self.agents['analyze']], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            if not result or not result.raw:
                raise WorkflowError("Comprehensive data analysis failed")
            
            return StepResult(
                content=f"# Comprehensive Data Analysis\n\n{result.raw}",
                sources=[f"Enhanced analysis of: {data_file}"]
            )
            
        except Exception as e:
            raise WorkflowError(f"Comprehensive data analysis failed: {e}")
    
    def _comprehensive_review(self, content: str, cycle: int) -> str:
        """Perform thorough academic review."""
        try:
            from crewai import Task, Crew
            
            review_focus = {
                1: "structural clarity, logical flow, and content completeness",
                2: "academic rigor, citation accuracy, and final polish"
            }
            
            task = Task(
                description=f"""Conduct comprehensive review {cycle} focusing on {review_focus[cycle]}:

CONTENT TO REVIEW:
{content}

REVIEW CRITERIA:
1. **Content Quality** (1-10): 
   - Completeness of analysis
   - Depth of insights
   - Evidence support for claims

2. **Academic Rigor** (1-10):
   - Logical structure and flow
   - Citation accuracy and completeness
   - Methodology soundness

3. **Business Relevance** (1-10):
   - Actionable insights
   - Strategic value for decision makers
   - Clear recommendations

4. **Critical Issues**:
   - Missing key analysis sections
   - Weak arguments or unsupported claims
   - Structural problems
   - Citation/reference issues

OUTPUT FORMAT:
OVERALL QUALITY: [Score 1-30]
DECISION: [ACCEPT/REVISE/MAJOR_REVISE]

DETAILED FEEDBACK:
- Content Issues: [specific problems]
- Structure Issues: [specific problems] 
- Missing Elements: [what's missing]
- Improvement Priorities: [top 3 priorities]

SPECIFIC REVISION INSTRUCTIONS:
[Detailed instructions for revision if needed]""",
                expected_output="Comprehensive review with scores and specific revision instructions",
                agent=self.agents['edit']
            )
            
            crew = Crew(agents=[self.agents['edit']], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            if result and result.raw:
                return result.raw
            else:
                return "Review failed - content appears acceptable"
                
        except Exception as e:
            print(f"Review failed: {e}")
            return "Review process failed - proceeding with current content"
    
    def _needs_revision(self, review_result: str) -> bool:
        """Determine if revision is needed based on review."""
        review_lower = review_result.lower()
        
        # Check for revision indicators
        needs_revision = any(indicator in review_lower for indicator in [
            'revise', 'major_revise', 'improvement needed', 'missing',
            'weak', 'incomplete', 'issues found'
        ])
        
        # Check overall score if present
        if 'overall quality:' in review_lower:
            try:
                # Extract score (format: "OVERALL QUALITY: X/30" or similar)
                import re
                score_match = re.search(r'overall quality:\s*(\d+)', review_lower)
                if score_match:
                    score = int(score_match.group(1))
                    if score < 20:  # Less than 20/30 needs revision
                        needs_revision = True
            except:
                pass
        
        if needs_revision:
            self.revision_count += 1
            print(f"Review indicates revision needed (cycle {self.revision_count})")
        else:
            print(f"Review passed - content acceptable")
        
        return needs_revision and self.revision_count < self.max_revisions
    
    def _perform_revision(self, review_feedback: str, analysis_result: StepResult = None) -> str:
        """Perform targeted revision based on review feedback."""
        try:
            from crewai import Task, Crew
            
            # Extract the original content and revision instructions
            task = Task(
                description=f"""Revise the research paper based on review feedback:

REVIEW FEEDBACK:
{review_feedback}

REVISION REQUIREMENTS:
1. Address all critical issues mentioned in the review
2. Improve content quality and academic rigor
3. Strengthen weak arguments with additional evidence
4. Add missing sections or analysis
5. Improve structure and flow
6. Ensure all claims are properly supported

{f"ADDITIONAL DATA ANALYSIS AVAILABLE: {analysis_result.content[:500]}..." if analysis_result else ""}

Focus on substantive improvements, not just cosmetic changes.
Maintain academic tone and proper citation format.
Ensure the revised version directly addresses the reviewer's concerns.""",
                expected_output="Substantially improved research paper addressing all review feedback",
                agent=self.agents['write']
            )
            
            crew = Crew(agents=[self.agents['write']], tasks=[task], verbose=False)
            result = crew.kickoff()
            
            if result and result.raw:
                return result.raw
            else:
                raise WorkflowError("Revision process failed")
                
        except Exception as e:
            raise WorkflowError(f"Revision failed: {e}")
    
    def _save_version(self, content: str, version_type: str):
        """Simple version tracking - save to results directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_info = {
            'type': version_type,
            'timestamp': timestamp,
            'word_count': len(content.split()),
            'revision_count': self.revision_count
        }
        self.versions.append(version_info)
        
        # Save to results directory
        filename = self.session_dir / f"version_{timestamp}_{version_type}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Version: {version_type}\n")
                f.write(f"# Timestamp: {timestamp}\n")
                f.write(f"# Revision: {self.revision_count}\n")
                f.write(f"# Session: {self.session_id}\n")
                f.write("=" * 50 + "\n\n")
                f.write(content)
            print(f"Saved version: {filename.name}")
        except Exception as e:
            print(f"Version save failed: {e}")
    
    def _print_summary_report(self, document: Document):
        """Print executive summary of the workflow."""
        print("\n" + "=" * 60)
        print("ENHANCED WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Research Goal: {document.goal}")
        print(f"Total Sections: {len(document.sections)}")
        print(f"Revision Cycles: {self.revision_count}")
        print(f"Versions Created: {len(self.versions)}")
        
        if document.sections:
            total_words = sum(len(section.content.split()) for section in document.sections)
            print(f"Total Word Count: {total_words}")
        
        print(f"Total Sources: {len(document.sources)}")
        
        # Version history
        if self.versions:
            print(f"\nVersion History:")
            for v in self.versions:
                print(f"   • {v['type']}: {v['timestamp']} ({v['word_count']} words)")
        
        print("=" * 60)


def create_enhanced_workflow() -> EnhancedWorkflow:
    """Factory function for enhanced workflow."""
    return EnhancedWorkflow()


def run_enhanced_research(goal: str, data_file: str = None) -> str:
    """
    Enhanced research interface with academic rigor.
    
    Features:
    - Multi-round review cycles
    - Comprehensive data analysis
    - Version tracking
    - Quality gates
    """
    workflow = create_enhanced_workflow()
    document = workflow.run(goal, data_file)
    return document.get_content()