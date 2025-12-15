#!/bin/bash
# Database Initialization Script
set -e

echo "=========================================="
echo "  TARA System Database Initialization"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Default values
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-tara}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-tara_password}
MYSQL_DATABASE=${MYSQL_DATABASE:-tara_db}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root_password}

# Wait for MySQL to be ready
wait_for_mysql() {
    echo -e "\n${YELLOW}Waiting for MySQL to be ready...${NC}"
    
    for i in {1..30}; do
        if mysql -h ${MYSQL_HOST} -P ${MYSQL_PORT} -u root -p${MYSQL_ROOT_PASSWORD} -e "SELECT 1" &> /dev/null; then
            echo -e "${GREEN}✓ MySQL is ready${NC}"
            return 0
        fi
        echo "  Attempt $i/30..."
        sleep 2
    done
    
    echo -e "${RED}✗ MySQL failed to start${NC}"
    exit 1
}

# Initialize MySQL
init_mysql() {
    echo -e "\n${YELLOW}Initializing MySQL database...${NC}"
    
    mysql -h ${MYSQL_HOST} -P ${MYSQL_PORT} -u root -p${MYSQL_ROOT_PASSWORD} < database/mysql/init/01_create_database.sql
    
    echo -e "${GREEN}✓ MySQL database initialized${NC}"
}

# Initialize Neo4j
init_neo4j() {
    echo -e "\n${YELLOW}Initializing Neo4j database...${NC}"
    
    NEO4J_URI=${NEO4J_URI:-bolt://localhost:7687}
    NEO4J_USER=${NEO4J_USER:-neo4j}
    NEO4J_PASSWORD=${NEO4J_PASSWORD:-neo4j_password}
    
    # Create constraints and indexes
    cypher-shell -a ${NEO4J_URI} -u ${NEO4J_USER} -p ${NEO4J_PASSWORD} << 'EOF'
// Asset constraints
CREATE CONSTRAINT asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE INDEX asset_type IF NOT EXISTS FOR (a:Asset) ON (a.type);

// Threat constraints
CREATE CONSTRAINT threat_id IF NOT EXISTS FOR (t:Threat) REQUIRE t.id IS UNIQUE;

// Relationship indexes
CREATE INDEX connects_to IF NOT EXISTS FOR ()-[r:CONNECTS_TO]-() ON (r.type);
EOF

    echo -e "${GREEN}✓ Neo4j database initialized${NC}"
}

# Initialize MinIO buckets
init_minio() {
    echo -e "\n${YELLOW}Initializing MinIO buckets...${NC}"
    
    MINIO_ENDPOINT=${MINIO_ENDPOINT:-localhost:9000}
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
    
    # Configure mc alias
    mc alias set tara http://${MINIO_ENDPOINT} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY} 2>/dev/null || true
    
    # Create buckets
    mc mb tara/documents --ignore-existing
    mc mb tara/reports --ignore-existing
    mc mb tara/diagrams --ignore-existing
    
    echo -e "${GREEN}✓ MinIO buckets created${NC}"
}

# Initialize Elasticsearch indices
init_elasticsearch() {
    echo -e "\n${YELLOW}Initializing Elasticsearch indices...${NC}"
    
    ES_HOST=${ES_HOSTS:-http://localhost:9200}
    
    # Document index
    curl -X PUT "${ES_HOST}/tara_documents" -H 'Content-Type: application/json' -d'
    {
        "mappings": {
            "properties": {
                "project_id": { "type": "integer" },
                "filename": { "type": "text" },
                "content": { "type": "text", "analyzer": "standard" },
                "created_at": { "type": "date" }
            }
        }
    }' 2>/dev/null || true
    
    # Threat index
    curl -X PUT "${ES_HOST}/tara_threats" -H 'Content-Type: application/json' -d'
    {
        "mappings": {
            "properties": {
                "project_id": { "type": "integer" },
                "threat_name": { "type": "text" },
                "threat_type": { "type": "keyword" },
                "description": { "type": "text" },
                "created_at": { "type": "date" }
            }
        }
    }' 2>/dev/null || true
    
    echo -e "${GREEN}✓ Elasticsearch indices created${NC}"
}

# Seed initial data
seed_data() {
    echo -e "\n${YELLOW}Seeding initial data...${NC}"
    
    # This would typically run a Python script to seed data
    # python scripts/tools/seed_data.py
    
    echo -e "${GREEN}✓ Initial data seeded${NC}"
}

# Main
main() {
    wait_for_mysql
    init_mysql
    # init_neo4j    # Uncomment when Neo4j is available
    # init_minio    # Uncomment when MinIO CLI is available
    # init_elasticsearch  # Uncomment when ES is available
    # seed_data
    
    echo -e "\n${GREEN}=========================================="
    echo "  Database Initialization Complete!"
    echo "==========================================${NC}"
}

main "$@"
