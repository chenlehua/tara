#!/bin/bash
# TARA System Installation Script
set -e

echo "=========================================="
echo "  TARA System Installation"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker installed${NC}"
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.11+${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 installed${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed. Please install Node.js 18+${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js installed${NC}"
}

# Setup environment
setup_environment() {
    echo -e "\n${YELLOW}Setting up environment...${NC}"
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    else
        echo -e "${YELLOW}⚠ .env file already exists${NC}"
    fi
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-jwt-key-change-in-production/${JWT_SECRET}/" .env
    echo -e "${GREEN}✓ Generated JWT secret${NC}"
}

# Start infrastructure
start_infrastructure() {
    echo -e "\n${YELLOW}Starting infrastructure services...${NC}"
    
    docker compose -f deploy/docker/docker-compose.yml up -d \
        mysql redis neo4j milvus-standalone elasticsearch minio
    
    echo -e "${GREEN}✓ Infrastructure services started${NC}"
    
    # Wait for services to be ready
    echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
    sleep 30
    
    echo -e "${GREEN}✓ Services are ready${NC}"
}

# Initialize database
init_database() {
    echo -e "\n${YELLOW}Initializing database...${NC}"
    
    # Run MySQL init script
    docker exec -i tara-mysql mysql -u root -proot_password < database/mysql/init/01_create_database.sql
    
    echo -e "${GREEN}✓ Database initialized${NC}"
}

# Install Python dependencies
install_python_deps() {
    echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Configure pip to use Chinese mirror
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    pip config set global.trusted-host mirrors.aliyun.com
    
    # Install shared module
    pip install -e backend/shared
    
    # Install service dependencies
    for service in project document asset threat-risk diagram report agent; do
        pip install -e backend/${service}-service
    done
    
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
}

# Install frontend dependencies
install_frontend_deps() {
    echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
    
    # Install pnpm if not exists
    if ! command -v pnpm &> /dev/null; then
        npm install -g pnpm --registry https://registry.npmmirror.com
    fi
    
    # Configure pnpm to use Chinese mirror
    pnpm config set registry https://registry.npmmirror.com
    
    cd frontend
    pnpm install
    cd ..
    
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
}

# Main
main() {
    check_prerequisites
    setup_environment
    start_infrastructure
    init_database
    install_python_deps
    install_frontend_deps
    
    echo -e "\n${GREEN}=========================================="
    echo "  Installation Complete!"
    echo "==========================================${NC}"
    echo ""
    echo "To start the system:"
    echo "  make backend-dev   # Start backend services"
    echo "  make frontend-dev  # Start frontend (in another terminal)"
    echo ""
    echo "Access the system at: http://localhost:3000"
}

main "$@"
