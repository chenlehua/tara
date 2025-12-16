"""
Neo4j Graph Database Connection
===============================

Neo4j driver for knowledge graph operations.
"""

from typing import Any, Dict, List, Optional

from neo4j import Driver, GraphDatabase, Session
from neo4j.exceptions import Neo4jError

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jDriver:
    """Neo4j driver wrapper with connection management."""

    _driver: Optional[Driver] = None
    _connection_error: Optional[str] = None

    @classmethod
    def get_driver(cls) -> Optional[Driver]:
        """Get Neo4j driver instance (singleton)."""
        if cls._driver is None and cls._connection_error is None:
            try:
                cls._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                )
                # Verify connectivity
                cls._driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
            except Exception as e:
                cls._connection_error = str(e)
                logger.warning(
                    f"Failed to connect to Neo4j: {e}. Graph operations will be unavailable."
                )
                cls._driver = None
        return cls._driver

    @classmethod
    def is_available(cls) -> bool:
        """Check if Neo4j is available."""
        return cls.get_driver() is not None

    @classmethod
    def close(cls) -> None:
        """Close Neo4j driver."""
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None
            cls._connection_error = None

    @classmethod
    def verify_connectivity(cls) -> bool:
        """Verify Neo4j connectivity."""
        driver = cls.get_driver()
        if driver is None:
            return False
        try:
            driver.verify_connectivity()
            return True
        except Neo4jError as e:
            logger.error(f"Neo4j connection failed: {e}")
            return False


def get_neo4j_driver() -> Optional[Driver]:
    """Get Neo4j driver for dependency injection."""
    return Neo4jDriver.get_driver()


# Lazy-initialized global driver
neo4j_driver: Optional[Driver] = None


def get_global_neo4j_driver() -> Optional[Driver]:
    """Get global Neo4j driver with lazy initialization."""
    global neo4j_driver
    if neo4j_driver is None:
        neo4j_driver = Neo4jDriver.get_driver()
    return neo4j_driver


def _get_neo4j_driver_internal() -> Optional[Driver]:
    """Internal function for getting driver."""
    return Neo4jDriver.get_driver()


class GraphService:
    """Service for graph database operations."""

    def __init__(self, driver: Driver = None):
        self._driver = driver
        self._lazy_driver = driver is None

    @property
    def driver(self) -> Optional[Driver]:
        """Get driver with lazy initialization."""
        if self._lazy_driver and self._driver is None:
            self._driver = get_neo4j_driver()
        return self._driver

    def is_available(self) -> bool:
        """Check if graph service is available."""
        return self.driver is not None

    def execute_query(
        self, query: str, parameters: Dict[str, Any] = None, database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if not self.is_available():
            logger.warning("Neo4j not available, returning empty results")
            return []
        with self.driver.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(
        self, query: str, parameters: Dict[str, Any] = None, database: str = "neo4j"
    ) -> Dict[str, Any]:
        """Execute a write query and return summary."""
        if not self.is_available():
            logger.warning("Neo4j not available, skipping write")
            return {
                "nodes_created": 0,
                "nodes_deleted": 0,
                "relationships_created": 0,
                "relationships_deleted": 0,
                "properties_set": 0,
            }
        with self.driver.session(database=database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "nodes_deleted": summary.counters.nodes_deleted,
                "relationships_created": summary.counters.relationships_created,
                "relationships_deleted": summary.counters.relationships_deleted,
                "properties_set": summary.counters.properties_set,
            }

    def create_node(
        self, label: str, properties: Dict[str, Any], database: str = "neo4j"
    ) -> Dict[str, Any]:
        """Create a node with given label and properties."""
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n, id(n) as node_id
        """
        results = self.execute_query(query, {"properties": properties}, database)
        return results[0] if results else {}

    def find_node(
        self,
        label: str,
        property_name: str,
        property_value: Any,
        database: str = "neo4j",
    ) -> Optional[Dict[str, Any]]:
        """Find a node by property."""
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        RETURN n, id(n) as node_id
        """
        results = self.execute_query(query, {"value": property_value}, database)
        return results[0] if results else None

    def create_relationship(
        self,
        from_label: str,
        from_property: str,
        from_value: Any,
        to_label: str,
        to_property: str,
        to_value: Any,
        rel_type: str,
        rel_properties: Dict[str, Any] = None,
        database: str = "neo4j",
    ) -> Dict[str, Any]:
        """Create a relationship between two nodes."""
        query = f"""
        MATCH (a:{from_label} {{{from_property}: $from_val}})
        MATCH (b:{to_label} {{{to_property}: $to_val}})
        CREATE (a)-[r:{rel_type} $properties]->(b)
        RETURN a, r, b
        """
        return self.execute_write(
            query,
            {
                "from_val": from_value,
                "to_val": to_value,
                "properties": rel_properties or {},
            },
            database,
        )

    def get_neighbors(
        self,
        label: str,
        property_name: str,
        property_value: Any,
        rel_type: str = None,
        direction: str = "both",
        database: str = "neo4j",
    ) -> List[Dict[str, Any]]:
        """Get neighboring nodes."""
        if direction == "outgoing":
            rel_pattern = f"-[r{':`'+rel_type+'`' if rel_type else ''}]->"
        elif direction == "incoming":
            rel_pattern = f"<-[r{':`'+rel_type+'`' if rel_type else ''}]-"
        else:
            rel_pattern = f"-[r{':`'+rel_type+'`' if rel_type else ''}]-"

        query = f"""
        MATCH (n:{label} {{{property_name}: $value}}){rel_pattern}(m)
        RETURN m, type(r) as relationship_type, id(m) as node_id
        """
        return self.execute_query(query, {"value": property_value}, database)


# Lazy-initialized global graph service
graph_service: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    """Get global graph service with lazy initialization."""
    global graph_service
    if graph_service is None:
        graph_service = GraphService()
    return graph_service
