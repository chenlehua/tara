#!/bin/bash
# TARA System Development Environment Setup
set -e

echo "=========================================="
echo "  TARA System Dev Environment Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

# Setup Python virtual environment
setup_python() {
    echo -e "\n${YELLOW}Setting up Python environment...${NC}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install development tools
    pip install pytest pytest-cov pytest-asyncio black isort mypy ruff
    
    # Install shared module in editable mode
    pip install -e backend/shared
    
    # Install all services in editable mode
    for service in project document asset threat-risk diagram report agent; do
        if [ -d "backend/${service}-service" ]; then
            pip install -e "backend/${service}-service"
        fi
    done
    
    echo -e "${GREEN}✓ Python environment ready${NC}"
}

# Setup frontend
setup_frontend() {
    echo -e "\n${YELLOW}Setting up frontend environment...${NC}"
    
    cd frontend
    npm install
    cd ..
    
    echo -e "${GREEN}✓ Frontend environment ready${NC}"
}

# Setup pre-commit hooks
setup_hooks() {
    echo -e "\n${YELLOW}Setting up Git hooks...${NC}"
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for TARA System

# Run Python linting
echo "Running Python linting..."
source venv/bin/activate
ruff check backend/ --fix
black backend/ --check
mypy backend/ --ignore-missing-imports

# Run frontend linting
echo "Running frontend linting..."
cd frontend && npm run lint
cd ..

echo "Pre-commit checks passed!"
EOF

    chmod +x .git/hooks/pre-commit
    
    echo -e "${GREEN}✓ Git hooks configured${NC}"
}

# Create VS Code settings
setup_vscode() {
    echo -e "\n${YELLOW}Setting up VS Code configuration...${NC}"
    
    mkdir -p .vscode
    
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "typescript.preferences.importModuleSpecifier": "relative",
    "editor.tabSize": 2,
    "[vue]": {
        "editor.defaultFormatter": "Vue.volar"
    }
}
EOF

    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Project Service",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload", "--port", "8001"],
            "cwd": "${workspaceFolder}/backend/project-service",
            "env": {"PYTHONPATH": "${workspaceFolder}/backend/shared"}
        },
        {
            "name": "Agent Service",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload", "--port", "8007"],
            "cwd": "${workspaceFolder}/backend/agent-service",
            "env": {"PYTHONPATH": "${workspaceFolder}/backend/shared"}
        }
    ]
}
EOF

    echo -e "${GREEN}✓ VS Code configuration ready${NC}"
}

# Main
main() {
    setup_python
    setup_frontend
    setup_hooks
    setup_vscode
    
    echo -e "\n${GREEN}=========================================="
    echo "  Development Environment Ready!"
    echo "==========================================${NC}"
    echo ""
    echo "Activate Python environment:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Start development servers:"
    echo "  make backend-dev   # All backend services"
    echo "  make frontend-dev  # Frontend dev server"
}

main "$@"
