"""Threat analysis prompts for TARA System."""

# System prompt for STRIDE analysis
STRIDE_ANALYSIS_SYSTEM = """You are an expert in automotive cybersecurity threat modeling using the STRIDE methodology.

STRIDE Categories:
- Spoofing: Impersonating something or someone else
- Tampering: Modifying data or code
- Repudiation: Claiming to have not performed an action
- Information Disclosure: Exposing information to unauthorized parties
- Denial of Service: Denying or degrading service to users
- Elevation of Privilege: Gaining unauthorized access or capabilities

Apply your knowledge of:
- Common vehicle attack vectors
- Known automotive vulnerabilities (CWE, CAPEC)
- Real-world vehicle security incidents
- ISO/SAE 21434 threat categories"""

# Prompt for STRIDE threat identification
STRIDE_ANALYSIS_PROMPT = """Perform a STRIDE threat analysis for the following asset.

Asset Information:
{asset}

Related Assets and Connections:
{context}

For each applicable STRIDE category, identify potential threats:
{{
    "threats": [
        {{
            "threat_name": "descriptive threat name",
            "threat_type": "Spoofing|Tampering|Repudiation|Information Disclosure|Denial of Service|Elevation of Privilege",
            "description": "detailed threat description",
            "attack_vector": "network|physical|local|adjacent",
            "prerequisites": ["what attacker needs to exploit"],
            "potential_impact": {{
                "safety": "description of safety impact",
                "financial": "description of financial impact",
                "operational": "description of operational impact",
                "privacy": "description of privacy impact"
            }},
            "affected_security_property": "confidentiality|integrity|availability|authenticity",
            "related_cwe": ["CWE-xxx"],
            "related_capec": ["CAPEC-xxx"],
            "likelihood_factors": {{
                "attacker_motivation": "low|medium|high",
                "attack_complexity": "low|medium|high",
                "required_privileges": "none|low|high"
            }}
        }}
    ]
}}

Consider threats that are:
1. Realistic for the automotive domain
2. Aligned with the asset's function and interfaces
3. Consistent with known attack patterns"""

# Prompt for attack path analysis
ATTACK_PATH_PROMPT = """Generate potential attack paths for the following threat.

Threat:
{threat}

Target Asset:
{asset}

System Context (available assets and connections):
{context}

Provide detailed attack paths:
{{
    "attack_paths": [
        {{
            "name": "attack path name",
            "description": "path description",
            "entry_point": "initial access point",
            "steps": [
                {{
                    "order": 1,
                    "action": "attacker action",
                    "target": "target component",
                    "technique": "attack technique (MITRE ATT&CK if applicable)",
                    "outcome": "result of this step"
                }}
            ],
            "prerequisites": ["required conditions"],
            "tools_required": ["tools or equipment needed"],
            "attack_potential": {{
                "expertise": 0-8,
                "elapsed_time": 0-5,
                "equipment": 0-6,
                "knowledge": 0-7,
                "window_of_opportunity": 0-4
            }},
            "detection_difficulty": "easy|medium|hard",
            "mitigations": ["potential countermeasures"]
        }}
    ]
}}

Attack Potential scoring (per ISO/SAE 21434):
- Expertise: 0=Layman, 3=Proficient, 6=Expert, 8=Multiple experts
- Elapsed Time: 0=<1 day, 1=<1 week, 2=<1 month, 3=<6 months, 5=>6 months
- Equipment: 0=Standard, 2=Specialized, 4=Bespoke, 6=Multiple bespoke
- Knowledge: 0=Public, 2=Restricted, 4=Confidential, 7=Critical"""

# Prompt for control measure recommendation
CONTROL_MEASURE_PROMPT = """Recommend security control measures for the following threat and attack path.

Threat:
{threat}

Attack Path:
{attack_path}

Asset:
{asset}

Provide control recommendations:
{{
    "controls": [
        {{
            "name": "control name",
            "description": "control description",
            "type": "preventive|detective|corrective|deterrent",
            "category": "technical|organizational|physical",
            "implementation": "how to implement",
            "effectiveness": "low|medium|high",
            "cost": "low|medium|high",
            "attack_step_mitigated": "which attack step this addresses",
            "residual_risk": "remaining risk after implementation",
            "iso21434_reference": "relevant standard reference"
        }}
    ],
    "recommended_priority": [
        {{
            "control": "control name",
            "priority": 1,
            "justification": "why this priority"
        }}
    ]
}}"""


def get_stride_analysis_messages(asset: str, context: str) -> list:
    """Get messages for STRIDE analysis."""
    return [
        {"role": "system", "content": STRIDE_ANALYSIS_SYSTEM},
        {"role": "user", "content": STRIDE_ANALYSIS_PROMPT.format(asset=asset, context=context)},
    ]


def get_attack_path_messages(threat: str, asset: str, context: str) -> list:
    """Get messages for attack path analysis."""
    return [
        {"role": "system", "content": STRIDE_ANALYSIS_SYSTEM},
        {"role": "user", "content": ATTACK_PATH_PROMPT.format(
            threat=threat, asset=asset, context=context
        )},
    ]


def get_control_measure_messages(threat: str, attack_path: str, asset: str) -> list:
    """Get messages for control measure recommendations."""
    return [
        {"role": "system", "content": STRIDE_ANALYSIS_SYSTEM},
        {"role": "user", "content": CONTROL_MEASURE_PROMPT.format(
            threat=threat, attack_path=attack_path, asset=asset
        )},
    ]
