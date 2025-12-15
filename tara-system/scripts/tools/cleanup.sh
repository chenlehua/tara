#!/bin/bash
# TARA System Cleanup Script
set -e

echo "=========================================="
echo "  TARA System Cleanup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

# Clean Python cache
clean_python() {
    echo -e "\n${YELLOW}Cleaning Python cache...${NC}"
    
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✓ Python cache cleaned${NC}"
}

# Clean Node.js cache
clean_node() {
    echo -e "\n${YELLOW}Cleaning Node.js cache...${NC}"
    
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
    fi
    if [ -d "frontend/dist" ]; then
        rm -rf frontend/dist
    fi
    rm -rf frontend/.vite 2>/dev/null || true
    
    echo -e "${GREEN}✓ Node.js cache cleaned${NC}"
}

# Clean Docker
clean_docker() {
    echo -e "\n${YELLOW}Cleaning Docker resources...${NC}"
    
    # Stop and remove containers
    docker-compose -f deploy/docker/docker-compose.yml down -v 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f 2>/dev/null || true
    
    # Remove dangling volumes
    docker volume prune -f 2>/dev/null || true
    
    echo -e "${GREEN}✓ Docker resources cleaned${NC}"
}

# Clean logs
clean_logs() {
    echo -e "\n${YELLOW}Cleaning log files...${NC}"
    
    find . -type f -name "*.log" -delete 2>/dev/null || true
    find . -type d -name "logs" -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✓ Log files cleaned${NC}"
}

# Clean temporary files
clean_temp() {
    echo -e "\n${YELLOW}Cleaning temporary files...${NC}"
    
    find . -type f -name "*.tmp" -delete 2>/dev/null || true
    find . -type f -name "*.swp" -delete 2>/dev/null || true
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✓ Temporary files cleaned${NC}"
}

# Clean all
clean_all() {
    clean_python
    clean_node
    clean_logs
    clean_temp
}

# Main
main() {
    case "${1:-all}" in
        python)
            clean_python
            ;;
        node)
            clean_node
            ;;
        docker)
            clean_docker
            ;;
        logs)
            clean_logs
            ;;
        temp)
            clean_temp
            ;;
        all)
            clean_all
            ;;
        deep)
            clean_all
            clean_docker
            ;;
        *)
            echo "Usage: $0 {python|node|docker|logs|temp|all|deep}"
            echo ""
            echo "Options:"
            echo "  python  - Clean Python cache files"
            echo "  node    - Clean Node.js dependencies and build"
            echo "  docker  - Clean Docker containers and volumes"
            echo "  logs    - Clean log files"
            echo "  temp    - Clean temporary files"
            echo "  all     - Clean all (except Docker)"
            echo "  deep    - Clean everything including Docker"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}=========================================="
    echo "  Cleanup Complete!"
    echo "==========================================${NC}"
}

main "$@"
