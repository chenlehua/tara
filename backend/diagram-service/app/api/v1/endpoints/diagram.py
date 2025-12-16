"""Diagram endpoints."""

from enum import Enum
from typing import Optional

from app.services.diagram_service import DiagramService
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from tara_shared.database import get_db
from tara_shared.utils import success_response

router = APIRouter()


def get_diagram_service(db: Session = Depends(get_db)) -> DiagramService:
    """Get diagram service with database session."""
    return DiagramService(db)


class DiagramType(str, Enum):
    """Diagram types."""

    ASSET_GRAPH = "asset_graph"
    ATTACK_TREE = "attack_tree"
    RISK_MATRIX = "risk_matrix"
    DATA_FLOW = "data_flow"
    ARCHITECTURE = "architecture"


class DiagramFormat(str, Enum):
    """Output formats."""

    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class DiagramRequest(BaseModel):
    """Diagram generation request."""

    project_id: int
    diagram_type: DiagramType
    format: DiagramFormat = DiagramFormat.PNG
    width: int = 1200
    height: int = 800
    options: Optional[dict] = None


@router.post("")
async def generate_diagram(
    request: DiagramRequest,
    diagram_service: DiagramService = Depends(get_diagram_service),
):
    """Generate a diagram."""
    result = await diagram_service.generate_diagram(
        project_id=request.project_id,
        diagram_type=request.diagram_type,
        format=request.format,
        width=request.width,
        height=request.height,
        options=request.options,
    )
    return success_response(result)


@router.get("/asset-graph/{project_id}")
async def get_asset_graph(
    project_id: int,
    format: DiagramFormat = Query(DiagramFormat.PNG),
    diagram_service: DiagramService = Depends(get_diagram_service),
):
    """Get asset graph diagram."""
    image_data = await diagram_service.generate_asset_graph(project_id, format)

    media_type = {
        DiagramFormat.PNG: "image/png",
        DiagramFormat.SVG: "image/svg+xml",
        DiagramFormat.PDF: "application/pdf",
    }[format]

    return StreamingResponse(
        image_data,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=asset_graph.{format.value}"},
    )


@router.get("/attack-tree/{threat_id}")
async def get_attack_tree(
    threat_id: int,
    format: DiagramFormat = Query(DiagramFormat.PNG),
    diagram_service: DiagramService = Depends(get_diagram_service),
):
    """Get attack tree diagram for a threat."""
    image_data = await diagram_service.generate_attack_tree(threat_id, format)

    media_type = {
        DiagramFormat.PNG: "image/png",
        DiagramFormat.SVG: "image/svg+xml",
        DiagramFormat.PDF: "application/pdf",
    }[format]

    return StreamingResponse(
        image_data,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=attack_tree.{format.value}"},
    )


@router.get("/risk-matrix/{project_id}")
async def get_risk_matrix(
    project_id: int,
    format: DiagramFormat = Query(DiagramFormat.PNG),
    diagram_service: DiagramService = Depends(get_diagram_service),
):
    """Get risk matrix diagram."""
    image_data = await diagram_service.generate_risk_matrix(project_id, format)

    media_type = {
        DiagramFormat.PNG: "image/png",
        DiagramFormat.SVG: "image/svg+xml",
        DiagramFormat.PDF: "application/pdf",
    }[format]

    return StreamingResponse(
        image_data,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=risk_matrix.{format.value}"},
    )


@router.get("/data-flow/{project_id}")
async def get_data_flow_diagram(
    project_id: int,
    format: DiagramFormat = Query(DiagramFormat.PNG),
    diagram_service: DiagramService = Depends(get_diagram_service),
):
    """Get data flow diagram."""
    image_data = await diagram_service.generate_data_flow(project_id, format)

    media_type = {
        DiagramFormat.PNG: "image/png",
        DiagramFormat.SVG: "image/svg+xml",
        DiagramFormat.PDF: "application/pdf",
    }[format]

    return StreamingResponse(
        image_data,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=data_flow.{format.value}"},
    )
