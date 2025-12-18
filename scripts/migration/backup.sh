#!/bin/bash
# Database Backup Script
set -e

echo "=========================================="
echo "  TARA System Database Backup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR=${BACKUP_DIR:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Default values
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-tara}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-tara_password}
MYSQL_DATABASE=${MYSQL_DATABASE:-tara_db}

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup MySQL
backup_mysql() {
    echo -e "\n${YELLOW}Backing up MySQL database...${NC}"
    
    BACKUP_FILE="${BACKUP_DIR}/mysql_${MYSQL_DATABASE}_${TIMESTAMP}.sql.gz"
    
    mysqldump -h ${MYSQL_HOST} -P ${MYSQL_PORT} -u ${MYSQL_USER} -p${MYSQL_PASSWORD} \
        ${MYSQL_DATABASE} | gzip > ${BACKUP_FILE}
    
    echo -e "${GREEN}✓ MySQL backup: ${BACKUP_FILE}${NC}"
}

# Backup Neo4j
backup_neo4j() {
    echo -e "\n${YELLOW}Backing up Neo4j database...${NC}"
    
    BACKUP_FILE="${BACKUP_DIR}/neo4j_${TIMESTAMP}.dump"
    
    # Neo4j backup requires admin access
    # neo4j-admin dump --database=neo4j --to=${BACKUP_FILE}
    
    echo -e "${YELLOW}⚠ Neo4j backup requires manual execution${NC}"
}

# Backup MinIO
backup_minio() {
    echo -e "\n${YELLOW}Backing up MinIO objects...${NC}"
    
    BACKUP_FILE="${BACKUP_DIR}/minio_${TIMESTAMP}.tar.gz"
    
    # Mirror all buckets
    mc mirror tara/ ${BACKUP_DIR}/minio_temp/ 2>/dev/null || true
    tar -czvf ${BACKUP_FILE} -C ${BACKUP_DIR} minio_temp 2>/dev/null || true
    rm -rf ${BACKUP_DIR}/minio_temp
    
    echo -e "${GREEN}✓ MinIO backup: ${BACKUP_FILE}${NC}"
}

# Cleanup old backups
cleanup_old_backups() {
    echo -e "\n${YELLOW}Cleaning up old backups...${NC}"
    
    # Keep last 7 days of backups
    find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete
    find ${BACKUP_DIR} -name "*.dump" -mtime +7 -delete
    find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
    
    echo -e "${GREEN}✓ Old backups cleaned${NC}"
}

# Main
main() {
    case "${1:-all}" in
        mysql)
            backup_mysql
            ;;
        neo4j)
            backup_neo4j
            ;;
        minio)
            backup_minio
            ;;
        all)
            backup_mysql
            backup_neo4j
            backup_minio
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        *)
            echo "Usage: $0 {mysql|neo4j|minio|all|cleanup}"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}=========================================="
    echo "  Backup Complete!"
    echo "==========================================${NC}"
    echo ""
    echo "Backup location: ${BACKUP_DIR}"
    ls -la ${BACKUP_DIR}
}

main "$@"
