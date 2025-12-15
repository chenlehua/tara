"""Report generation prompts for TARA System."""

# System prompt for report writing
REPORT_WRITER_SYSTEM = """You are an expert technical writer specializing in automotive cybersecurity documentation.
Your task is to generate professional TARA reports that comply with ISO/SAE 21434 standards.

Your writing should be:
- Clear and precise
- Technically accurate
- Well-structured
- Appropriate for both technical and management audiences"""

# Prompt for executive summary
EXECUTIVE_SUMMARY_PROMPT = """Write an executive summary for a TARA report based on the following data.

Project Information:
{project}

Key Statistics:
{statistics}

Major Findings:
{findings}

Write a 2-3 paragraph executive summary that:
1. Introduces the scope and purpose of the assessment
2. Summarizes key findings and risk levels
3. Provides high-level recommendations

Format the summary professionally for C-level executives."""

# Prompt for section writing
WRITE_SECTION_PROMPT = """Write the following section of a TARA report.

Section: {section_name}
Template: {template}

Data:
{data}

Requirements:
- Follow the ISO/SAE 21434 structure
- Include all relevant data points
- Use tables where appropriate
- Maintain professional technical language

Write the complete section content."""

# Prompt for risk summary
RISK_SUMMARY_PROMPT = """Generate a risk summary section for the TARA report.

Threats and Risks:
{threats}

Risk Distribution:
{risk_distribution}

Create a risk summary that includes:
1. Overview of identified risks
2. Risk distribution by severity
3. Risk distribution by STRIDE category
4. Key risk factors and trends
5. Comparison with industry benchmarks (if applicable)

Include a risk heat map description and key risk indicators."""

# Prompt for recommendations
RECOMMENDATIONS_PROMPT = """Generate cybersecurity recommendations based on the TARA findings.

Identified Risks:
{risks}

Control Measures:
{controls}

Generate recommendations in priority order:
{{
    "recommendations": [
        {{
            "priority": "critical|high|medium|low",
            "title": "recommendation title",
            "description": "detailed description",
            "rationale": "why this is recommended",
            "addressed_risks": ["list of addressed risks"],
            "implementation_effort": "low|medium|high",
            "timeline": "immediate|short-term|long-term",
            "responsible_party": "who should implement",
            "success_criteria": "how to measure success"
        }}
    ],
    "implementation_roadmap": {{
        "phase1": ["immediate actions"],
        "phase2": ["short-term actions"],
        "phase3": ["long-term actions"]
    }}
}}"""

# Prompt for compliance mapping
COMPLIANCE_MAPPING_PROMPT = """Map the TARA findings to regulatory requirements.

Findings:
{findings}

Map to the following standards and regulations:
- ISO/SAE 21434
- UN R155/R156
- TISAX (if applicable)

Provide a compliance matrix:
{{
    "compliance_matrix": [
        {{
            "requirement_id": "requirement identifier",
            "requirement_text": "requirement description",
            "status": "compliant|partially_compliant|non_compliant|not_applicable",
            "evidence": "evidence of compliance",
            "gaps": "identified gaps if any",
            "remediation": "suggested remediation"
        }}
    ],
    "compliance_summary": {{
        "iso21434": "X% compliant",
        "unr155": "X% compliant"
    }}
}}"""


def get_executive_summary_messages(project: str, statistics: str, findings: str) -> list:
    """Get messages for executive summary generation."""
    return [
        {"role": "system", "content": REPORT_WRITER_SYSTEM},
        {"role": "user", "content": EXECUTIVE_SUMMARY_PROMPT.format(
            project=project, statistics=statistics, findings=findings
        )},
    ]


def get_section_writing_messages(section_name: str, template: str, data: str) -> list:
    """Get messages for section writing."""
    return [
        {"role": "system", "content": REPORT_WRITER_SYSTEM},
        {"role": "user", "content": WRITE_SECTION_PROMPT.format(
            section_name=section_name, template=template, data=data
        )},
    ]


def get_recommendations_messages(risks: str, controls: str) -> list:
    """Get messages for recommendations generation."""
    return [
        {"role": "system", "content": REPORT_WRITER_SYSTEM},
        {"role": "user", "content": RECOMMENDATIONS_PROMPT.format(
            risks=risks, controls=controls
        )},
    ]


# Section templates for different report types
SECTION_TEMPLATES = {
    "iso21434": {
        "sections": [
            "Executive Summary",
            "1. Introduction",
            "2. Scope Definition",
            "3. Item Definition",
            "4. Asset Identification",
            "5. Threat Scenario Identification",
            "6. Impact Assessment",
            "7. Attack Path Analysis",
            "8. Attack Feasibility Assessment",
            "9. Risk Determination",
            "10. Risk Treatment Decision",
            "11. Cybersecurity Goals",
            "12. Cybersecurity Requirements",
            "Appendix A: Asset Catalog",
            "Appendix B: Threat Catalog",
            "Appendix C: Risk Register",
        ]
    },
    "simple": {
        "sections": [
            "Executive Summary",
            "1. Project Overview",
            "2. Assets",
            "3. Threats and Risks",
            "4. Recommendations",
            "Appendix: Detailed Findings",
        ]
    },
}
