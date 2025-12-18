"""TARA System AI prompts."""

from .document_analysis import (
    DOCUMENT_PARSER_SYSTEM,
    EXTRACT_STRUCTURE_PROMPT,
    EXTRACT_TECHNICAL_CONTENT_PROMPT,
    PROCESS_OCR_RESULT_PROMPT,
    ANALYZE_DIAGRAM_PROMPT,
    get_document_parser_messages,
    get_technical_extraction_messages,
    get_ocr_processing_messages,
)

from .asset_discovery import (
    ASSET_DISCOVERY_SYSTEM,
    IDENTIFY_ASSETS_PROMPT,
    IDENTIFY_RELATIONSHIPS_PROMPT,
    DAMAGE_SCENARIO_PROMPT,
    get_asset_discovery_messages,
    get_relationship_messages,
    get_damage_scenario_messages,
)

from .threat_analysis import (
    STRIDE_ANALYSIS_SYSTEM,
    STRIDE_ANALYSIS_PROMPT,
    ATTACK_PATH_PROMPT,
    CONTROL_MEASURE_PROMPT,
    get_stride_analysis_messages,
    get_attack_path_messages,
    get_control_measure_messages,
)

from .report_generation import (
    REPORT_WRITER_SYSTEM,
    EXECUTIVE_SUMMARY_PROMPT,
    WRITE_SECTION_PROMPT,
    RISK_SUMMARY_PROMPT,
    RECOMMENDATIONS_PROMPT,
    COMPLIANCE_MAPPING_PROMPT,
    SECTION_TEMPLATES,
    get_executive_summary_messages,
    get_section_writing_messages,
    get_recommendations_messages,
)

__all__ = [
    # Document analysis
    "DOCUMENT_PARSER_SYSTEM",
    "EXTRACT_STRUCTURE_PROMPT",
    "get_document_parser_messages",
    "get_technical_extraction_messages",
    "get_ocr_processing_messages",
    
    # Asset discovery
    "ASSET_DISCOVERY_SYSTEM",
    "IDENTIFY_ASSETS_PROMPT",
    "get_asset_discovery_messages",
    "get_relationship_messages",
    "get_damage_scenario_messages",
    
    # Threat analysis
    "STRIDE_ANALYSIS_SYSTEM",
    "STRIDE_ANALYSIS_PROMPT",
    "get_stride_analysis_messages",
    "get_attack_path_messages",
    "get_control_measure_messages",
    
    # Report generation
    "REPORT_WRITER_SYSTEM",
    "SECTION_TEMPLATES",
    "get_executive_summary_messages",
    "get_section_writing_messages",
    "get_recommendations_messages",
]
