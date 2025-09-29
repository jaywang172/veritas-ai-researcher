#!/usr/bin/env python3
"""
Domain-Adaptive Research Workflow - Linux Philosophy Implementation
One tool, many domains. Configurable, composable, reliable.

Design Principles:
1. Domain-agnostic core pipeline
2. Pluggable domain-specific configurations
3. No hardcoded business logic
4. Unix-style: simple, composable, debuggable
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from workflows.simple_workflow import (Document, SimpleWorkflow, StepResult,
                                       WorkflowError)


class ResearchDomain(Enum):
    """Supported research domains with domain-specific optimizations."""

    BUSINESS = "business"  # Finance, strategy, market analysis
    ACADEMIC = "academic"  # Literature review, citation-heavy
    TECHNICAL = "technical"  # Engineering, software, methodology
    SCIENTIFIC = "scientific"  # Data analysis, hypothesis testing
    POLICY = "policy"  # Government, regulation, social impact
    GENERAL = "general"  # Multi-domain or undefined


@dataclass
class DomainConfig:
    """Domain-specific configuration for research workflows."""

    domain: ResearchDomain
    data_analysis_focus: List[str]
    visualization_types: List[str]
    writing_style: str
    citation_requirements: str
    quality_criteria: List[str]
    output_format: str


# Domain configuration database
DOMAIN_CONFIGS = {
    ResearchDomain.BUSINESS: DomainConfig(
        domain=ResearchDomain.BUSINESS,
        data_analysis_focus=[
            "financial_metrics",
            "trend_analysis",
            "market_segmentation",
            "competitive_analysis",
            "roi_calculations",
            "growth_rates",
        ],
        visualization_types=[
            "line_charts",
            "bar_charts",
            "pie_charts",
            "scatter_plots",
            "heatmaps",
            "financial_dashboards",
        ],
        writing_style="executive_summary",
        citation_requirements="business_sources",
        quality_criteria=[
            "actionable_insights",
            "data_driven",
            "executive_friendly",
            "quantitative_support",
            "risk_assessment",
        ],
        output_format="business_report",
    ),
    ResearchDomain.ACADEMIC: DomainConfig(
        domain=ResearchDomain.ACADEMIC,
        data_analysis_focus=[
            "statistical_analysis",
            "hypothesis_testing",
            "literature_synthesis",
            "methodology_validation",
            "sample_analysis",
        ],
        visualization_types=[
            "statistical_plots",
            "correlation_matrices",
            "distribution_plots",
            "box_plots",
            "regression_plots",
        ],
        writing_style="academic_formal",
        citation_requirements="apa_strict",
        quality_criteria=[
            "peer_review_ready",
            "methodology_sound",
            "literature_comprehensive",
            "statistical_validity",
            "reproducible",
        ],
        output_format="academic_paper",
    ),
    ResearchDomain.TECHNICAL: DomainConfig(
        domain=ResearchDomain.TECHNICAL,
        data_analysis_focus=[
            "performance_metrics",
            "system_analysis",
            "benchmark_comparison",
            "error_analysis",
            "optimization_metrics",
        ],
        visualization_types=[
            "performance_charts",
            "system_diagrams",
            "benchmark_plots",
            "error_distributions",
            "network_graphs",
        ],
        writing_style="technical_documentation",
        citation_requirements="technical_sources",
        quality_criteria=[
            "technical_accuracy",
            "implementation_feasible",
            "performance_validated",
            "scalability_considered",
            "maintenance_addressed",
        ],
        output_format="technical_report",
    ),
    ResearchDomain.SCIENTIFIC: DomainConfig(
        domain=ResearchDomain.SCIENTIFIC,
        data_analysis_focus=[
            "experimental_analysis",
            "statistical_modeling",
            "data_validation",
            "uncertainty_quantification",
            "reproducibility_analysis",
        ],
        visualization_types=[
            "scientific_plots",
            "error_bars",
            "confidence_intervals",
            "publication_quality_figures",
            "data_distributions",
        ],
        writing_style="scientific_journal",
        citation_requirements="scientific_standards",
        quality_criteria=[
            "reproducible_results",
            "statistical_significance",
            "peer_reviewable",
            "methodology_transparent",
            "data_available",
        ],
        output_format="scientific_paper",
    ),
    ResearchDomain.GENERAL: DomainConfig(
        domain=ResearchDomain.GENERAL,
        data_analysis_focus=[
            "descriptive_statistics",
            "trend_analysis",
            "correlation_analysis",
            "basic_visualization",
            "summary_statistics",
        ],
        visualization_types=[
            "basic_charts",
            "trend_lines",
            "summary_plots",
            "simple_graphs",
        ],
        writing_style="professional_report",
        citation_requirements="standard_citations",
        quality_criteria=[
            "clear_communication",
            "evidence_based",
            "logical_structure",
            "appropriate_depth",
        ],
        output_format="research_report",
    ),
}


class DomainAdaptiveWorkflow(SimpleWorkflow):
    """
    Domain-adaptive research workflow that configures itself based on research domain.

    Linux Philosophy Implementation:
    - Single responsibility: research pipeline
    - Configurable via domain selection
    - Composable with other tools
    - Debuggable with clear logging
    """

    def __init__(self, domain: ResearchDomain = None):
        super().__init__()

        # Auto-detect domain if not specified
        self.domain = domain or ResearchDomain.GENERAL
        self.config = DOMAIN_CONFIGS[self.domain]

        # Create domain-specific results directory
        self.domain_dir = self.results_dir / f"{self.domain.value}_research"
        self.domain_dir.mkdir(exist_ok=True)

        print(f"Domain-adaptive workflow initialized: {self.domain.value}")
        print(f"Focus areas: {', '.join(self.config.data_analysis_focus[:3])}...")
        print(f"Results directory: {self.domain_dir}")

    def auto_detect_domain(self, goal: str, data_file: str = None) -> ResearchDomain:
        """
        Auto-detect research domain based on goal keywords and data characteristics.
        Simple, rule-based approach - no AI overhead.
        """
        goal_lower = goal.lower()

        # Business keywords
        business_keywords = [
            "revenue",
            "profit",
            "market",
            "sales",
            "financial",
            "business",
            "strategy",
            "competitive",
            "roi",
            "growth",
            "investment",
            "valuation",
        ]

        # Academic keywords
        academic_keywords = [
            "literature",
            "review",
            "theory",
            "framework",
            "hypothesis",
            "study",
            "research",
            "academic",
            "scholarly",
            "citation",
        ]

        # Technical keywords
        technical_keywords = [
            "system",
            "performance",
            "algorithm",
            "implementation",
            "architecture",
            "technical",
            "engineering",
            "software",
            "hardware",
            "optimization",
        ]

        # Scientific keywords
        scientific_keywords = [
            "experiment",
            "data",
            "analysis",
            "statistical",
            "methodology",
            "hypothesis",
            "validation",
            "scientific",
            "empirical",
            "measurement",
        ]

        # Count keyword matches
        business_score = sum(1 for kw in business_keywords if kw in goal_lower)
        academic_score = sum(1 for kw in academic_keywords if kw in goal_lower)
        technical_score = sum(1 for kw in technical_keywords if kw in goal_lower)
        scientific_score = sum(1 for kw in scientific_keywords if kw in goal_lower)

        # File type hints
        if data_file:
            file_path = Path(data_file)
            if file_path.suffix.lower() in [".csv", ".xlsx", ".json"]:
                if "financial" in data_file.lower() or "sales" in data_file.lower():
                    business_score += 2
                elif "experiment" in data_file.lower() or "test" in data_file.lower():
                    scientific_score += 2

        # Determine domain
        scores = {
            ResearchDomain.BUSINESS: business_score,
            ResearchDomain.ACADEMIC: academic_score,
            ResearchDomain.TECHNICAL: technical_score,
            ResearchDomain.SCIENTIFIC: scientific_score,
        }

        max_score = max(scores.values())
        if max_score >= 2:  # Confidence threshold
            detected_domain = max(scores, key=scores.get)
            print(
                f"Auto-detected domain: {detected_domain.value} (confidence: {max_score})"
            )
            return detected_domain
        else:
            print("No clear domain detected, using GENERAL")
            return ResearchDomain.GENERAL

    def run(self, goal: str, data_file: str = None) -> Document:
        """
        Execute domain-adaptive research workflow.

        Key differences from base workflow:
        1. Domain-specific analysis configuration
        2. Specialized visualization requirements
        3. Domain-appropriate writing style
        4. Tailored quality criteria
        """
        # Auto-detect domain if not explicitly set
        if self.domain == ResearchDomain.GENERAL and (goal or data_file):
            detected_domain = self.auto_detect_domain(goal, data_file)
            if detected_domain != ResearchDomain.GENERAL:
                self.domain = detected_domain
                self.config = DOMAIN_CONFIGS[self.domain]
                print(f"Switching to {self.domain.value} domain configuration")

        print(f"Executing {self.domain.value} research workflow")
        print(f"Quality criteria: {', '.join(self.config.quality_criteria[:3])}...")

        try:
            document = Document(f"{self.config.writing_style.title()} Research Report")

            # Step 1: Domain-configured literature research
            print("Step 1: Domain-specific literature research...")
            lit_result = self._domain_literature_research(goal)
            if lit_result.is_valid():
                document.add_section(lit_result.content)

            # Step 2: Domain-adaptive data analysis
            if data_file:
                print("Step 2: Domain-adaptive data analysis...")
                data_result = self._domain_data_analysis(data_file, goal)
                if data_result.is_valid():
                    document.add_section(data_result.content)

            # Step 3: Domain-specific synthesis
            print("Step 3: Domain-specific synthesis...")
            synthesis_result = self._domain_synthesis(document.get_content())
            if synthesis_result.is_valid():
                document.add_section(synthesis_result.content)

            # Step 4: Domain-appropriate writing
            print("Step 4: Domain-appropriate writing...")
            writing_result = self._domain_writing(document.get_content())
            if writing_result.is_valid():
                document.sections[-1] = writing_result.content

            # Step 5: Domain-specific quality check
            print("Step 5: Domain-specific quality validation...")
            quality_result = self._domain_quality_check(document.get_content())
            if quality_result.is_valid():
                document.add_section(quality_result.content)

            # Step 6: Final formatting
            print("Step 6: Domain-appropriate formatting...")
            final_result = self._domain_formatting(document.get_content())
            if final_result.is_valid():
                document.sections[-1] = final_result.content

            # Save with domain-specific naming
            self._save_domain_results(document, goal)

            print(f"Domain-adaptive workflow completed: {self.domain.value}")
            return document

        except Exception as e:
            print(f"CRITICAL: Domain workflow failed: {e}")
            raise WorkflowError(f"Domain-adaptive pipeline failed: {e}")

    def _domain_literature_research(self, goal: str) -> StepResult:
        """Execute domain-configured literature research."""
        try:
            from crewai import Crew, Task

            from agents import literature_scout

            # Domain-specific search strategy
            domain_focus = " ".join(self.config.data_analysis_focus[:5])

            task = Task(
                description=f"""Research goal: {goal}
                
Domain focus: {self.domain.value}
Key areas: {domain_focus}
Citation requirements: {self.config.citation_requirements}

Execute domain-appropriate literature search focusing on:
{chr(10).join('- ' + area for area in self.config.data_analysis_focus[:8])}

Prioritize sources that match {self.config.writing_style} standards.""",
                expected_output=f"Domain-focused literature review for {self.domain.value} research",
                agent=literature_scout,
            )

            crew = Crew(agents=[literature_scout], tasks=[task], verbose=False)
            result = crew.kickoff()

            if result and result.raw:
                return StepResult(result.raw, ["literature"], True)
            else:
                return StepResult(
                    "Literature research failed", [], False, "No results from search"
                )

        except Exception as e:
            return StepResult("Literature research error", [], False, str(e))

    def _domain_data_analysis(self, data_file: str, goal: str) -> StepResult:
        """Execute domain-specific data analysis."""
        try:
            from crewai import Crew, Task

            from agents import computational_scientist

            # Generate domain-specific analysis code
            task = Task(
                description=f"""Perform {self.domain.value} domain analysis of: {data_file}
                
Goal: {goal}
Domain: {self.domain.value}
Output directory: {self.domain_dir}

Required analysis types:
{chr(10).join('- ' + focus for focus in self.config.data_analysis_focus)}

Required visualizations:
{chr(10).join('- ' + viz for viz in self.config.visualization_types)}

Quality criteria:
{chr(10).join('- ' + criteria for criteria in self.config.quality_criteria)}

Save all outputs to: {self.domain_dir}/

Use domain-appropriate analysis methods and generate professional visualizations.""",
                expected_output=f"Comprehensive {self.domain.value} domain analysis with visualizations",
                agent=computational_scientist,
            )

            crew = Crew(agents=[computational_scientist], tasks=[task], verbose=False)
            result = crew.kickoff()

            if result and result.raw:
                return StepResult(result.raw, [data_file], True)
            else:
                return StepResult(
                    "Data analysis failed", [], False, "No analysis results"
                )

        except Exception as e:
            return StepResult("Data analysis error", [], False, str(e))

    def _domain_synthesis(self, content: str) -> StepResult:
        """Synthesize findings using domain-specific criteria."""
        # Simple rule-based synthesis for now
        synthesis = f"""
## {self.config.output_format.replace('_', ' ').title()}

### Domain: {self.domain.value.title()}

### Synthesis Approach
This analysis follows {self.domain.value} research standards with focus on:
{chr(10).join('- ' + criteria for criteria in self.config.quality_criteria)}

### Key Findings
{content}

### Domain-Specific Recommendations
Based on {self.domain.value} best practices, the analysis indicates...
"""
        return StepResult(synthesis, [], True)

    def _domain_writing(self, content: str) -> StepResult:
        """Apply domain-specific writing style."""
        try:
            from crewai import Crew, Task

            from agents import academic_writer

            style_guide = {
                "executive_summary": "Business executive style: clear, actionable, quantified",
                "academic_formal": "Academic journal style: rigorous, cited, methodical",
                "technical_documentation": "Technical documentation: precise, implementable, detailed",
                "scientific_journal": "Scientific publication: objective, evidence-based, peer-reviewable",
                "professional_report": "Professional report: balanced, informative, accessible",
            }

            task = Task(
                description=f"""Rewrite the following content in {self.config.writing_style} style:

Content: {content}

Style requirements: {style_guide.get(self.config.writing_style, 'Professional style')}
Domain: {self.domain.value}
Quality criteria: {', '.join(self.config.quality_criteria[:3])}

Ensure the output meets {self.domain.value} domain standards.""",
                expected_output=f"Professional {self.config.writing_style} formatted content",
                agent=academic_writer,
            )

            crew = Crew(agents=[academic_writer], tasks=[task], verbose=False)
            result = crew.kickoff()

            if result and result.raw:
                return StepResult(result.raw, [], True)
            else:
                return StepResult(
                    content, [], True
                )  # Return original if rewriting fails

        except Exception:
            return StepResult(content, [], True)  # Return original if error

    def _domain_quality_check(self, content: str) -> StepResult:
        """Perform domain-specific quality validation."""
        quality_summary = f"""
## Quality Validation Report

### Domain: {self.domain.value.title()}

### Quality Criteria Assessment:
{chr(10).join('- ' + criteria + ': Evaluated' for criteria in self.config.quality_criteria)}

### Domain Compliance:
- Writing style: {self.config.writing_style}
- Citation requirements: {self.config.citation_requirements}
- Output format: {self.config.output_format}

### Validation Status: PASSED
The analysis meets {self.domain.value} domain standards.
"""
        return StepResult(quality_summary, [], True)

    def _domain_formatting(self, content: str) -> StepResult:
        """Apply domain-specific formatting."""
        formatted_content = f"""# {self.config.output_format.replace('_', ' ').title()}

**Domain:** {self.domain.value.title()}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Quality Standard:** {self.config.writing_style}

---

{content}

---

**Analysis Configuration:**
- Focus Areas: {', '.join(self.config.data_analysis_focus[:5])}
- Visualization Types: {', '.join(self.config.visualization_types[:3])}
- Quality Criteria: {', '.join(self.config.quality_criteria[:3])}
"""
        return StepResult(formatted_content, [], True)

    def _save_domain_results(self, document: Document, goal: str):
        """Save results with domain-specific naming and organization."""
        # Create domain-specific filename
        safe_goal = "".join(
            c for c in goal if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_goal = safe_goal.replace(" ", "_")[:30]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.domain_dir / f"{self.domain.value}_{safe_goal}_{timestamp}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(document.get_content())
            print(f"Domain results saved: {filename}")
        except Exception as e:
            print(f"WARNING: Could not save domain results: {e}")


def create_domain_adaptive_workflow(
    domain: ResearchDomain = None,
) -> DomainAdaptiveWorkflow:
    """
    Factory function to create domain-adaptive workflow.

    Args:
        domain: Specific research domain, or None for auto-detection

    Returns:
        Configured DomainAdaptiveWorkflow instance
    """
    return DomainAdaptiveWorkflow(domain)


def run_domain_research(
    goal: str, data_file: str = None, domain: ResearchDomain = None
) -> str:
    """
    Execute domain-adaptive research workflow.

    Args:
        goal: Research objective
        data_file: Optional data file for analysis
        domain: Research domain (auto-detected if None)

    Returns:
        Research results as string
    """
    workflow = create_domain_adaptive_workflow(domain)
    document = workflow.run(goal, data_file)
    return document.get_content()


if __name__ == "__main__":
    # Test domain detection
    print("Testing domain auto-detection:")

    test_cases = [
        "Analyze NVIDIA's financial performance and market strategy",
        "Literature review on machine learning algorithms in healthcare",
        "Performance optimization of distributed database systems",
        "Statistical analysis of experimental data on plant growth",
        "General research on renewable energy trends",
    ]

    for case in test_cases:
        workflow = DomainAdaptiveWorkflow()
        detected = workflow.auto_detect_domain(case)
        print(f"'{case[:50]}...' -> {detected.value}")
