#!/bin/bash
# TARA System Health Check Script
set -e

echo "=========================================="
echo "  TARA System Health Check"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BASE_URL=${BASE_URL:-http://localhost}

# Service definitions
declare -A SERVICES=(
    ["project-service"]="8001"
    ["document-service"]="8002"
    ["asset-service"]="8003"
    ["threat-risk-service"]="8004"
    ["diagram-service"]="8005"
    ["report-service"]="8006"
    ["agent-service"]="8007"
)

# Infrastructure definitions
declare -A INFRA=(
    ["mysql"]="3306"
    ["redis"]="6379"
    ["neo4j"]="7687"
    ["milvus"]="19530"
    ["elasticsearch"]="9200"
    ["minio"]="9000"
)

# Check service health
check_service() {
    local name=$1
    local port=$2
    local url="${BASE_URL}:${port}/health"
    
    if curl -s -o /dev/null -w "%{http_code}" ${url} | grep -q "200"; then
        echo -e "  ${GREEN}✓${NC} ${name}: healthy"
        return 0
    else
        echo -e "  ${RED}✗${NC} ${name}: unhealthy"
        return 1
    fi
}

# Check port availability
check_port() {
    local name=$1
    local port=$2
    
    if nc -z localhost ${port} 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} ${name}: port ${port} open"
        return 0
    else
        echo -e "  ${RED}✗${NC} ${name}: port ${port} closed"
        return 1
    fi
}

# Check backend services
check_services() {
    echo -e "\n${YELLOW}Checking backend services...${NC}"
    
    local all_healthy=true
    for service in "${!SERVICES[@]}"; do
        if ! check_service "${service}" "${SERVICES[$service]}"; then
            all_healthy=false
        fi
    done
    
    return $([ "$all_healthy" = true ] && echo 0 || echo 1)
}

# Check infrastructure
check_infrastructure() {
    echo -e "\n${YELLOW}Checking infrastructure...${NC}"
    
    local all_healthy=true
    for infra in "${!INFRA[@]}"; do
        if ! check_port "${infra}" "${INFRA[$infra]}"; then
            all_healthy=false
        fi
    done
    
    return $([ "$all_healthy" = true ] && echo 0 || echo 1)
}

# Check disk space
check_disk() {
    echo -e "\n${YELLOW}Checking disk space...${NC}"
    
    local usage=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
    
    if [ ${usage} -lt 80 ]; then
        echo -e "  ${GREEN}✓${NC} Disk usage: ${usage}%"
    elif [ ${usage} -lt 90 ]; then
        echo -e "  ${YELLOW}⚠${NC} Disk usage: ${usage}% (warning)"
    else
        echo -e "  ${RED}✗${NC} Disk usage: ${usage}% (critical)"
    fi
}

# Check memory
check_memory() {
    echo -e "\n${YELLOW}Checking memory...${NC}"
    
    local total=$(free -m | awk 'NR==2 {print $2}')
    local used=$(free -m | awk 'NR==2 {print $3}')
    local percent=$((used * 100 / total))
    
    if [ ${percent} -lt 80 ]; then
        echo -e "  ${GREEN}✓${NC} Memory usage: ${percent}% (${used}MB / ${total}MB)"
    elif [ ${percent} -lt 90 ]; then
        echo -e "  ${YELLOW}⚠${NC} Memory usage: ${percent}% (warning)"
    else
        echo -e "  ${RED}✗${NC} Memory usage: ${percent}% (critical)"
    fi
}

# Check Docker containers
check_docker() {
    echo -e "\n${YELLOW}Checking Docker containers...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Docker not available"
        return
    fi
    
    local running=$(docker ps --format "{{.Names}}" | grep tara | wc -l)
    local total=$(docker ps -a --format "{{.Names}}" | grep tara | wc -l)
    
    echo -e "  Running containers: ${running}/${total}"
    
    docker ps --filter "name=tara" --format "  {{.Names}}: {{.Status}}"
}

# Main
main() {
    local exit_code=0
    
    check_infrastructure || exit_code=1
    check_services || exit_code=1
    check_disk
    check_memory
    check_docker
    
    echo ""
    if [ ${exit_code} -eq 0 ]; then
        echo -e "${GREEN}=========================================="
        echo "  All systems healthy!"
        echo "==========================================${NC}"
    else
        echo -e "${RED}=========================================="
        echo "  Some systems are unhealthy!"
        echo "==========================================${NC}"
    fi
    
    exit ${exit_code}
}

main "$@"
