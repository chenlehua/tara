#!/bin/bash
# TARA System Deployment Script
set -e

echo "=========================================="
echo "  TARA System Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-dev}
NAMESPACE="tara-${ENVIRONMENT}"

echo -e "\n${YELLOW}Deploying to environment: ${ENVIRONMENT}${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}kubectl is not installed${NC}"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites met${NC}"
}

# Create namespace
create_namespace() {
    echo -e "\n${YELLOW}Creating namespace...${NC}"
    
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    echo -e "${GREEN}✓ Namespace ${NAMESPACE} ready${NC}"
}

# Deploy infrastructure
deploy_infra() {
    echo -e "\n${YELLOW}Deploying infrastructure...${NC}"
    
    kubectl apply -f ../k8s/base/infra/ -n ${NAMESPACE}
    
    # Wait for infrastructure to be ready
    echo "Waiting for MySQL..."
    kubectl wait --for=condition=ready pod -l app=mysql -n ${NAMESPACE} --timeout=300s
    
    echo "Waiting for Redis..."
    kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=60s
    
    echo -e "${GREEN}✓ Infrastructure deployed${NC}"
}

# Deploy AI models
deploy_ai_models() {
    echo -e "\n${YELLOW}Deploying AI models...${NC}"
    
    kubectl apply -f ../k8s/base/ai-models/ -n ${NAMESPACE}
    
    echo -e "${GREEN}✓ AI models deployment initiated${NC}"
    echo -e "${YELLOW}Note: AI models may take several minutes to start${NC}"
}

# Deploy application
deploy_application() {
    echo -e "\n${YELLOW}Deploying application...${NC}"
    
    # Use Kustomize with overlay
    kubectl apply -k ../k8s/overlays/${ENVIRONMENT}
    
    # Wait for deployments
    for service in project document asset threat-risk diagram report agent; do
        echo "Waiting for ${service}-service..."
        kubectl wait --for=condition=available deployment/${ENVIRONMENT}-${service}-service \
            -n ${NAMESPACE} --timeout=120s || true
    done
    
    echo -e "${GREEN}✓ Application deployed${NC}"
}

# Deploy monitoring
deploy_monitoring() {
    echo -e "\n${YELLOW}Deploying monitoring...${NC}"
    
    kubectl apply -f ../monitoring/ -n ${NAMESPACE}
    
    echo -e "${GREEN}✓ Monitoring deployed${NC}"
}

# Show status
show_status() {
    echo -e "\n${YELLOW}Deployment Status:${NC}"
    
    echo -e "\nPods:"
    kubectl get pods -n ${NAMESPACE}
    
    echo -e "\nServices:"
    kubectl get services -n ${NAMESPACE}
    
    echo -e "\nIngress:"
    kubectl get ingress -n ${NAMESPACE}
}

# Rollback
rollback() {
    echo -e "\n${YELLOW}Rolling back deployment...${NC}"
    
    for service in project document asset threat-risk diagram report agent; do
        kubectl rollout undo deployment/${ENVIRONMENT}-${service}-service -n ${NAMESPACE} || true
    done
    
    echo -e "${GREEN}✓ Rollback initiated${NC}"
}

# Main
main() {
    case "${2:-deploy}" in
        deploy)
            check_prerequisites
            create_namespace
            deploy_infra
            deploy_ai_models
            deploy_application
            deploy_monitoring
            show_status
            ;;
        infra)
            check_prerequisites
            create_namespace
            deploy_infra
            ;;
        app)
            check_prerequisites
            deploy_application
            ;;
        ai)
            check_prerequisites
            deploy_ai_models
            ;;
        monitoring)
            check_prerequisites
            deploy_monitoring
            ;;
        status)
            show_status
            ;;
        rollback)
            rollback
            ;;
        *)
            echo "Usage: $0 <environment> <command>"
            echo ""
            echo "Environments: dev, staging, prod"
            echo ""
            echo "Commands:"
            echo "  deploy      - Full deployment"
            echo "  infra       - Deploy infrastructure only"
            echo "  app         - Deploy application only"
            echo "  ai          - Deploy AI models only"
            echo "  monitoring  - Deploy monitoring only"
            echo "  status      - Show deployment status"
            echo "  rollback    - Rollback application"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}=========================================="
    echo "  Deployment Complete!"
    echo "==========================================${NC}"
}

main "$@"
