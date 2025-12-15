"""Diagram generation service."""
import io
from typing import Optional, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

from tara_shared.utils import get_logger

logger = get_logger(__name__)


class DiagramService:
    """Service for generating various diagrams."""

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
        # Create sample graph
        G = nx.DiGraph()
        
        # Sample nodes (in real implementation, fetch from Neo4j)
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
            G, pos, ax=ax,
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
        
        # Sample attack tree structure
        G = nx.DiGraph()
        
        # Add nodes (goal at top, sub-goals, then leaves)
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
            G, pos, ax=ax,
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
        
        # Risk matrix (5x4: impact x likelihood)
        # Values represent risk level: 1=negligible, 2=low, 3=medium, 4=high, 5=critical
        matrix = np.array([
            [3, 4, 5, 5],  # Severe
            [2, 3, 4, 5],  # Major
            [1, 2, 3, 4],  # Moderate
            [1, 1, 2, 3],  # Minor
            [1, 1, 1, 2],  # Negligible
        ])
        
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
                ax.text(j, i, risk_labels[value - 1], ha="center", va="center",
                       fontsize=11, color=text_color, fontweight="bold")
        
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
        
        # Sample data flow nodes
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
            G, pos, ax=ax,
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
