"""Asset discovery prompts for TARA System."""

# System prompt for asset identification
ASSET_DISCOVERY_SYSTEM = """You are an expert in automotive cybersecurity asset identification.
Your task is to identify and categorize vehicle assets based on technical documentation.

You understand:
- Vehicle E/E architecture
- ECU types and functions
- Communication buses (CAN, LIN, FlexRay, Ethernet)
- External interfaces (OBD, Bluetooth, WiFi, Cellular)
- Data assets and their sensitivity levels

Apply the CIA triad (Confidentiality, Integrity, Availability) to assess security attributes."""

# Prompt for asset identification
IDENTIFY_ASSETS_PROMPT = """Based on the following technical content, identify all cybersecurity-relevant assets.

Content:
{content}

For each asset, provide:
{{
    "assets": [
        {{
            "name": "asset name",
            "type": "ecu|gateway|bus|sensor|actuator|external_interface|data|function",
            "category": "powertrain|chassis|adas|connectivity|infotainment|body",
            "description": "brief description",
            "security_attributes": {{
                "confidentiality": "low|medium|high",
                "integrity": "low|medium|high",
                "availability": "low|medium|high"
            }},
            "interfaces": [
                {{
                    "name": "interface name",
                    "type": "CAN|LIN|FlexRay|Ethernet|Bluetooth|WiFi|Cellular|USB",
                    "direction": "in|out|bidirectional"
                }}
            ],
            "safety_relevance": "none|low|medium|high|critical",
            "justification": "why this asset is security-relevant"
        }}
    ]
}}

Focus on assets that:
1. Process or store sensitive data
2. Control safety-critical functions
3. Interface with external networks
4. Can be accessed by potential attackers"""

# Prompt for relationship identification
IDENTIFY_RELATIONSHIPS_PROMPT = """Analyze the following assets and identify their relationships.

Assets:
{assets}

For each relationship, provide:
{{
    "relationships": [
        {{
            "source": "source asset name",
            "target": "target asset name",
            "type": "connects_to|sends_data_to|controls|monitors|authenticates",
            "protocol": "communication protocol if applicable",
            "data_type": "type of data exchanged",
            "trust_level": "trusted|untrusted|semi-trusted"
        }}
    ],
    "trust_boundaries": [
        {{
            "name": "boundary name",
            "assets_inside": ["list of assets"],
            "assets_outside": ["list of assets"],
            "crossing_points": ["interfaces that cross the boundary"]
        }}
    ]
}}"""

# Prompt for damage scenario identification
DAMAGE_SCENARIO_PROMPT = """For the following asset, identify potential damage scenarios.

Asset:
{asset}

Consider the following damage categories:
- Safety (S): Physical harm to drivers, passengers, or road users
- Financial (F): Direct financial loss, repair costs, liability
- Operational (O): Loss of vehicle functionality or availability
- Privacy (P): Exposure of personal or sensitive data

Provide damage scenarios in this format:
{{
    "damage_scenarios": [
        {{
            "name": "scenario name",
            "description": "detailed description",
            "safety_impact": "negligible|minor|moderate|major|severe",
            "financial_impact": "negligible|minor|moderate|major|severe",
            "operational_impact": "negligible|minor|moderate|major|severe",
            "privacy_impact": "negligible|minor|moderate|major|severe",
            "affected_stakeholders": ["driver", "passengers", "manufacturer", "third_parties"],
            "regulatory_implications": ["relevant regulations if any"]
        }}
    ]
}}"""


def get_asset_discovery_messages(content: str) -> list:
    """Get messages for asset discovery."""
    return [
        {"role": "system", "content": ASSET_DISCOVERY_SYSTEM},
        {"role": "user", "content": IDENTIFY_ASSETS_PROMPT.format(content=content)},
    ]


def get_relationship_messages(assets: str) -> list:
    """Get messages for relationship identification."""
    return [
        {"role": "system", "content": ASSET_DISCOVERY_SYSTEM},
        {"role": "user", "content": IDENTIFY_RELATIONSHIPS_PROMPT.format(assets=assets)},
    ]


def get_damage_scenario_messages(asset: str) -> list:
    """Get messages for damage scenario identification."""
    return [
        {"role": "system", "content": ASSET_DISCOVERY_SYSTEM},
        {"role": "user", "content": DAMAGE_SCENARIO_PROMPT.format(asset=asset)},
    ]
