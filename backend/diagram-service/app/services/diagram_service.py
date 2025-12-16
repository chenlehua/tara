"""Diagram generation service."""

import io
from typing import Any, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from sqlalchemy.orm import Session
from tara_shared.models import Asset, ThreatRisk
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class DiagramService:
    """Service for generating various diagrams."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def _get_assets_from_db(self, project_id: int) -> List[Asset]:
        """Fetch assets from database."""
        if not self.db:
            return []
        try:
            return self.db.query(Asset).filter(Asset.project_id == project_id).all()
        except Exception as e:
            logger.error(f"Failed to fetch assets: {e}")
            return []

    def _get_threats_from_db(self, project_id: int) -> List[ThreatRisk]:
        """Fetch threats from database."""
        if not self.db:
            return []
        try:
            return (
                self.db.query(ThreatRisk).filter(ThreatRisk.project_id == project_id).all()
            )
        except Exception as e:
            logger.error(f"Failed to fetch threats: {e}")
            return []

    async def generate_diagram(
        self,
        project_id: int,
        diagram_type: str,
        format: str = "png",
        width: int = 1200,
        height: int = 800,
        options: Optional[dict] = None,
    ) -> dict:
        """Generate a diagram."""
        # Map diagram type to generator method
        generators = {
            "asset_graph": self.generate_asset_graph,
            "attack_tree": self.generate_attack_tree,
            "risk_matrix": self.generate_risk_matrix,
            "data_flow": self.generate_data_flow,
        }

        generator = generators.get(diagram_type)
        if not generator:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

        # TODO: Actually save to MinIO and return URL
        return {
            "type": diagram_type,
            "format": format,
            "url": f"/api/v1/diagrams/{diagram_type}/{project_id}?format={format}",
        }

    async def generate_asset_graph(
        self,
        project_id: int,
        format: str = "png",
    ) -> io.BytesIO:
        """Generate asset relationship graph."""
        G = nx.DiGraph()

        # Fetch assets from database
        db_assets = self._get_assets_from_db(project_id)

        if db_assets:
            # Use real data from database
            type_colors = {
                "ecu": "#e6a23c",
                "gateway": "#409eff",
                "sensor": "#67c23a",
                "actuator": "#909399",
                "external": "#f56c6c",
                "bus": "#67c23a",
            }

            nodes = []
            edges = []

            for asset in db_assets:
                asset_type = (asset.asset_type or "ecu").lower()
                color = type_colors.get(asset_type, "#409eff")
                nodes.append((asset.name, {"type": asset_type, "color": color}))

                # Create parent-child edges
                if asset.parent_id:
                    parent = next(
                        (a for a in db_assets if a.id == asset.parent_id), None
                    )
                    if parent:
                        edges.append((parent.name, asset.name))

            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
        else:
            # Fallback to sample data if no assets in database
            nodes = [
                ("Gateway", {"type": "gateway", "color": "#409eff"}),
                ("CAN Bus", {"type": "bus", "color": "#67c23a"}),
                ("Engine ECU", {"type": "ecu", "color": "#e6a23c"}),
                ("Brake ECU", {"type": "ecu", "color": "#e6a23c"}),
                ("ADAS ECU", {"type": "ecu", "color": "#e6a23c"}),
                ("Telematics", {"type": "external", "color": "#f56c6c"}),
            ]

            edges = [
                ("Gateway", "CAN Bus"),
                ("CAN Bus", "Engine ECU"),
                ("CAN Bus", "Brake ECU"),
                ("CAN Bus", "ADAS ECU"),
                ("Gateway", "Telematics"),
            ]

            G.add_nodes_from(nodes)
            G.add_edges_from(edges)

        # Generate visualization
        fig, ax = plt.subplots(figsize=(12, 8), dpi=100)

        pos = nx.spring_layout(G, k=2, iterations=50)
        node_colors = [G.nodes[n].get("color", "#409eff") for n in G.nodes()]

        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_color=node_colors,
            node_size=3000,
            font_size=10,
            font_weight="bold",
            edge_color="#c0c4cc",
            arrows=True,
            arrowsize=20,
        )

        ax.set_title("资产关系图", fontsize=16, fontweight="bold")

        # Legend
        legend_elements = [
            mpatches.Patch(color="#409eff", label="网关"),
            mpatches.Patch(color="#67c23a", label="总线"),
            mpatches.Patch(color="#e6a23c", label="ECU"),
            mpatches.Patch(color="#f56c6c", label="外部接口"),
        ]
        ax.legend(handles=legend_elements, loc="upper left")

        plt.tight_layout()

        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight", dpi=100)
        buffer.seek(0)
        plt.close(fig)

        return buffer

    async def generate_attack_tree(
        self,
        threat_id: int,
        format: str = "png",
    ) -> io.BytesIO:
        """Generate attack tree diagram."""
        fig, ax = plt.subplots(figsize=(14, 10), dpi=100)

        G = nx.DiGraph()

        # Try to fetch threat from database
        threat = None
        if self.db:
            try:
                threat = (
                    self.db.query(ThreatRisk).filter(ThreatRisk.id == threat_id).first()
                )
            except Exception as e:
                logger.error(f"Failed to fetch threat: {e}")

        if threat:
            # Build attack tree from threat data
            goal_label = threat.threat_name or "攻击目标"
            G.add_node("Goal", level=0, label=goal_label)

            # Parse attack paths if available
            attack_paths = threat.attack_paths if hasattr(threat, "attack_paths") else []
            if attack_paths:
                for i, path in enumerate(attack_paths):
                    path_id = f"A{i+1}"
                    path_label = path.name if hasattr(path, "name") else f"攻击路径{i+1}"
                    G.add_node(path_id, level=1, label=path_label)
                    G.add_edge("Goal", path_id)

                    # Add steps as leaves
                    steps = path.steps if hasattr(path, "steps") and path.steps else []
                    for j, step in enumerate(steps):
                        step_id = f"A{i+1}.{j+1}"
                        step_label = step.get("action", f"步骤{j+1}") if isinstance(step, dict) else str(step)
                        G.add_node(step_id, level=2, label=step_label)
                        G.add_edge(path_id, step_id)
            else:
                # Generate default nodes based on threat type
                attack_vector = threat.attack_vector or "未知"
                G.add_node("A1", level=1, label=f"利用{attack_vector}")
                G.add_node("A1.1", level=2, label="获取访问权限")
                G.add_node("A1.2", level=2, label="执行攻击")
                G.add_edge("Goal", "A1")
                G.add_edge("A1", "A1.1")
                G.add_edge("A1", "A1.2")
        else:
            # Fallback to sample attack tree structure
            G.add_node("Goal", level=0, label="获取车辆控制权")
            G.add_node("A1", level=1, label="入侵OBD接口")
            G.add_node("A2", level=1, label="攻击远程服务")
            G.add_node("A1.1", level=2, label="物理接入OBD")
            G.add_node("A1.2", level=2, label="绕过认证")
            G.add_node("A2.1", level=2, label="中间人攻击")
            G.add_node("A2.2", level=2, label="服务器漏洞")

            edges = [
                ("Goal", "A1"),
                ("Goal", "A2"),
                ("A1", "A1.1"),
                ("A1", "A1.2"),
                ("A2", "A2.1"),
                ("A2", "A2.2"),
            ]
            G.add_edges_from(edges)

        # Hierarchical layout
        pos = {}
        levels = {0: ["Goal"], 1: ["A1", "A2"], 2: ["A1.1", "A1.2", "A2.1", "A2.2"]}

        for level, nodes in levels.items():
            y = 1 - level * 0.4
            for i, node in enumerate(nodes):
                x = (i + 1) / (len(nodes) + 1)
                pos[node] = (x, y)

        # Draw
        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=False,
            node_color=["#f56c6c"] + ["#e6a23c"] * 2 + ["#67c23a"] * 4,
            node_size=2500,
            edge_color="#606266",
            arrows=True,
            arrowsize=15,
        )

        # Add labels
        labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=9, ax=ax)

        ax.set_title("攻击树分析", fontsize=16, fontweight="bold")
        ax.axis("off")

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight", dpi=100)
        buffer.seek(0)
        plt.close(fig)

        return buffer

    async def generate_risk_matrix(
        self,
        project_id: int,
        format: str = "png",
    ) -> io.BytesIO:
        """Generate risk matrix heatmap."""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

        # Base risk matrix (5x4: impact x likelihood)
        # Values represent risk level: 1=negligible, 2=low, 3=medium, 4=high, 5=critical
        matrix = np.array(
            [
                [3, 4, 5, 5],  # Severe
                [2, 3, 4, 5],  # Major
                [1, 2, 3, 4],  # Moderate
                [1, 1, 2, 3],  # Minor
                [1, 1, 1, 2],  # Negligible
            ]
        )

        # Count threats in each cell if database is available
        threat_counts = np.zeros((5, 4), dtype=int)
        db_threats = self._get_threats_from_db(project_id)

        if db_threats:
            for threat in db_threats:
                # Map impact level (1-4) to row index (0-4, inverted)
                impact = threat.impact_level if threat.impact_level else 2
                impact_idx = 4 - min(max(impact, 1), 5)  # Invert for matrix display

                # Map likelihood (1-4) to column index
                likelihood = threat.likelihood if threat.likelihood else 2
                likelihood_idx = min(max(likelihood - 1, 0), 3)

                threat_counts[impact_idx, likelihood_idx] += 1

        # Color map
        colors = ["#f4f4f5", "#67c23a", "#409eff", "#e6a23c", "#f56c6c"]
        from matplotlib.colors import ListedColormap

        cmap = ListedColormap(colors)

        im = ax.imshow(matrix, cmap=cmap, vmin=1, vmax=5, aspect="auto")

        # Labels
        impact_labels = ["严重", "重大", "中等", "轻微", "可忽略"]
        likelihood_labels = ["低", "中", "高", "非常高"]

        ax.set_xticks(range(len(likelihood_labels)))
        ax.set_yticks(range(len(impact_labels)))
        ax.set_xticklabels(likelihood_labels, fontsize=11)
        ax.set_yticklabels(impact_labels, fontsize=11)

        ax.set_xlabel("可能性 (Likelihood)", fontsize=12, fontweight="bold")
        ax.set_ylabel("影响程度 (Impact)", fontsize=12, fontweight="bold")
        ax.set_title("风险矩阵 (ISO/SAE 21434)", fontsize=14, fontweight="bold")

        # Add text annotations
        risk_labels = ["可忽略", "低", "中", "高", "严重"]
        for i in range(len(impact_labels)):
            for j in range(len(likelihood_labels)):
                value = matrix[i, j]
                text_color = "white" if value >= 4 else "black"
                count = threat_counts[i, j]
                # Show risk level and threat count if available
                if count > 0:
                    label_text = f"{risk_labels[value - 1]}\n({count})"
                else:
                    label_text = risk_labels[value - 1]
                ax.text(
                    j,
                    i,
                    label_text,
                    ha="center",
                    va="center",
                    fontsize=10,
                    color=text_color,
                    fontweight="bold",
                )

        # Legend
        legend_elements = [
            mpatches.Patch(color="#f56c6c", label="严重 (Critical)"),
            mpatches.Patch(color="#e6a23c", label="高 (High)"),
            mpatches.Patch(color="#409eff", label="中 (Medium)"),
            mpatches.Patch(color="#67c23a", label="低 (Low)"),
            mpatches.Patch(color="#f4f4f5", label="可忽略 (Negligible)"),
        ]
        ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1))

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight", dpi=100)
        buffer.seek(0)
        plt.close(fig)

        return buffer

    async def generate_data_flow(
        self,
        project_id: int,
        format: str = "png",
    ) -> io.BytesIO:
        """Generate data flow diagram."""
        fig, ax = plt.subplots(figsize=(14, 10), dpi=100)

        G = nx.DiGraph()

        # Fetch assets from database
        db_assets = self._get_assets_from_db(project_id)

        if db_assets:
            # Use real data from database
            type_colors = {
                "ecu": "#f56c6c",
                "gateway": "#e6a23c",
                "sensor": "#67c23a",
                "actuator": "#909399",
                "external": "#409eff",
                "user": "#67c23a",
                "cloud": "#409eff",
            }

            nodes = []
            edges = []

            for asset in db_assets:
                asset_type = (asset.asset_type or "ecu").lower()
                color = type_colors.get(asset_type, "#409eff")
                nodes.append((asset.name, {"shape": "rect", "color": color}))

                # Create edges based on interfaces
                interfaces = asset.interfaces or []
                for iface in interfaces:
                    if isinstance(iface, dict):
                        iface_type = iface.get("type", "")
                        # Find connected assets with matching interface
                        for other_asset in db_assets:
                            if other_asset.id != asset.id:
                                other_interfaces = other_asset.interfaces or []
                                for other_iface in other_interfaces:
                                    if isinstance(other_iface, dict):
                                        if other_iface.get("type") == iface_type:
                                            edges.append(
                                                (
                                                    asset.name,
                                                    other_asset.name,
                                                    {"label": iface_type},
                                                )
                                            )
                                            break

            # Add parent-child edges if no interface edges
            if not edges:
                for asset in db_assets:
                    if asset.parent_id:
                        parent = next(
                            (a for a in db_assets if a.id == asset.parent_id), None
                        )
                        if parent:
                            edges.append((parent.name, asset.name, {"label": "包含"}))

            G.add_nodes_from(nodes)
            G.add_edges_from([(e[0], e[1]) for e in edges])
        else:
            # Fallback to sample data flow nodes
            nodes = [
                ("User", {"shape": "ellipse", "color": "#67c23a"}),
                ("Mobile App", {"shape": "rect", "color": "#409eff"}),
                ("Cloud Server", {"shape": "rect", "color": "#409eff"}),
                ("TSP", {"shape": "rect", "color": "#e6a23c"}),
                ("Gateway", {"shape": "rect", "color": "#e6a23c"}),
                ("ECU", {"shape": "rect", "color": "#f56c6c"}),
            ]

            edges = [
                ("User", "Mobile App", {"label": "控制指令"}),
                ("Mobile App", "Cloud Server", {"label": "HTTPS"}),
                ("Cloud Server", "TSP", {"label": "API调用"}),
                ("TSP", "Gateway", {"label": "远程命令"}),
                ("Gateway", "ECU", {"label": "CAN消息"}),
            ]

            G.add_nodes_from(nodes)
            G.add_edges_from([(e[0], e[1]) for e in edges])

        pos = {
            "User": (0, 0.5),
            "Mobile App": (0.2, 0.5),
            "Cloud Server": (0.4, 0.5),
            "TSP": (0.6, 0.5),
            "Gateway": (0.8, 0.5),
            "ECU": (1.0, 0.5),
        }

        node_colors = [G.nodes[n].get("color", "#409eff") for n in G.nodes()]

        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_color=node_colors,
            node_size=4000,
            font_size=10,
            font_weight="bold",
            edge_color="#606266",
            arrows=True,
            arrowsize=20,
            node_shape="s",
        )

        # Edge labels
        edge_labels = {(e[0], e[1]): e[2]["label"] for e in edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=9, ax=ax)

        ax.set_title("数据流图", fontsize=16, fontweight="bold")
        ax.axis("off")

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight", dpi=100)
        buffer.seek(0)
        plt.close(fig)

        return buffer
