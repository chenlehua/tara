"""Document analysis prompts for TARA System."""

# System prompt for document parsing
DOCUMENT_PARSER_SYSTEM = """You are an expert automotive cybersecurity document analyzer.
Your task is to extract structured information from technical documents related to vehicle systems.

Focus on identifying:
1. System architecture and components
2. Communication interfaces and protocols
3. Data flows and trust boundaries
4. Security-relevant features and mechanisms

Output your analysis in a structured JSON format."""

# Prompt for extracting document structure
EXTRACT_STRUCTURE_PROMPT = """Analyze the following document content and extract its hierarchical structure.

Document content:
{content}

Extract the following information in JSON format:
{{
    "title": "document title",
    "type": "specification|design|requirement|manual|other",
    "sections": [
        {{
            "title": "section title",
            "level": 1,
            "content_summary": "brief summary",
            "subsections": [...]
        }}
    ],
    "key_topics": ["list of main topics"],
    "referenced_standards": ["ISO 21434", "UN R155", etc.]
}}"""

# Prompt for extracting technical content
EXTRACT_TECHNICAL_CONTENT_PROMPT = """Extract technical information from the following document section.

Section content:
{content}

Identify and extract:
{{
    "components": [
        {{
            "name": "component name",
            "type": "ECU|sensor|actuator|gateway|bus|interface",
            "description": "component description",
            "interfaces": ["list of interfaces"]
        }}
    ],
    "protocols": ["communication protocols mentioned"],
    "data_flows": [
        {{
            "source": "source component",
            "destination": "destination component",
            "data_type": "type of data",
            "protocol": "communication protocol"
        }}
    ],
    "security_features": ["security mechanisms mentioned"]
}}"""

# Prompt for OCR result processing
PROCESS_OCR_RESULT_PROMPT = """Process the following OCR-extracted text from a vehicle technical document.
Clean up any OCR errors and structure the content appropriately.

OCR Text:
{ocr_text}

Provide:
1. Corrected text with proper formatting
2. Identified tables and their structure
3. Extracted diagrams descriptions
4. Key technical terms and their definitions

Output in JSON format:
{{
    "cleaned_text": "corrected and formatted text",
    "tables": [...],
    "diagrams": [...],
    "terminology": {{}}
}}"""

# Prompt for diagram analysis (multimodal)
ANALYZE_DIAGRAM_PROMPT = """Analyze this vehicle system diagram and extract the following information:

1. Identify all components shown in the diagram
2. Map the connections between components
3. Identify communication buses and protocols
4. Note any security boundaries or trust zones

Provide your analysis in JSON format:
{{
    "diagram_type": "architecture|data_flow|network|other",
    "components": [
        {{
            "name": "component name",
            "type": "type",
            "position": "description of position in diagram"
        }}
    ],
    "connections": [
        {{
            "from": "source",
            "to": "destination",
            "type": "connection type",
            "protocol": "if identifiable"
        }}
    ],
    "security_zones": ["identified security zones"],
    "trust_boundaries": ["identified trust boundaries"]
}}"""


def get_document_parser_messages(content: str) -> list:
    """Get messages for document parsing."""
    return [
        {"role": "system", "content": DOCUMENT_PARSER_SYSTEM},
        {"role": "user", "content": EXTRACT_STRUCTURE_PROMPT.format(content=content)},
    ]


def get_technical_extraction_messages(content: str) -> list:
    """Get messages for technical content extraction."""
    return [
        {"role": "system", "content": DOCUMENT_PARSER_SYSTEM},
        {"role": "user", "content": EXTRACT_TECHNICAL_CONTENT_PROMPT.format(content=content)},
    ]


def get_ocr_processing_messages(ocr_text: str) -> list:
    """Get messages for OCR result processing."""
    return [
        {"role": "system", "content": DOCUMENT_PARSER_SYSTEM},
        {"role": "user", "content": PROCESS_OCR_RESULT_PROMPT.format(ocr_text=ocr_text)},
    ]
