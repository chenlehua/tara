#!/bin/bash
# Build Docker images for TARA System
set -e

echo "=========================================="
echo "  TARA System Image Build"
echo "=========================================="

# Configuration
REGISTRY=${REGISTRY:-""}
VERSION=${VERSION:-$(git describe --tags --always --dirty 2>/dev/null || echo "latest")}
PUSH=${PUSH:-false}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_ROOT}"

# Image prefix
if [ -n "${REGISTRY}" ]; then
    IMAGE_PREFIX="${REGISTRY}/tara-system"
else
    IMAGE_PREFIX="tara-system"
fi

echo -e "\n${YELLOW}Building images with tag: ${VERSION}${NC}"
echo -e "Registry: ${REGISTRY:-local}"

# Build backend services
build_backend() {
    echo -e "\n${YELLOW}Building backend services...${NC}"
    
    # Build base image with shared module
    docker build -t ${IMAGE_PREFIX}/backend-base:${VERSION} \
        -f deploy/docker/dockerfiles/backend.Dockerfile \
        --target base \
        backend/
    
    # Build individual services
    for service in project document asset threat-risk diagram report agent; do
        echo -e "\nBuilding ${service}-service..."
        
        docker build -t ${IMAGE_PREFIX}/${service}-service:${VERSION} \
            -f backend/${service}-service/Dockerfile \
            --build-arg VERSION=${VERSION} \
            backend/
        
        echo -e "${GREEN}✓ Built ${service}-service:${VERSION}${NC}"
    done
}

# Build frontend
build_frontend() {
    echo -e "\n${YELLOW}Building frontend...${NC}"
    
    docker build -t ${IMAGE_PREFIX}/frontend:${VERSION} \
        -f deploy/docker/dockerfiles/frontend.Dockerfile \
        --build-arg VERSION=${VERSION} \
        frontend/
    
    echo -e "${GREEN}✓ Built frontend:${VERSION}${NC}"
}

# Push images
push_images() {
    if [ "${PUSH}" = "true" ] && [ -n "${REGISTRY}" ]; then
        echo -e "\n${YELLOW}Pushing images to registry...${NC}"
        
        for service in project document asset threat-risk diagram report agent; do
            docker push ${IMAGE_PREFIX}/${service}-service:${VERSION}
            
            # Also tag as latest
            docker tag ${IMAGE_PREFIX}/${service}-service:${VERSION} \
                       ${IMAGE_PREFIX}/${service}-service:latest
            docker push ${IMAGE_PREFIX}/${service}-service:latest
        done
        
        docker push ${IMAGE_PREFIX}/frontend:${VERSION}
        docker tag ${IMAGE_PREFIX}/frontend:${VERSION} ${IMAGE_PREFIX}/frontend:latest
        docker push ${IMAGE_PREFIX}/frontend:latest
        
        echo -e "${GREEN}✓ Images pushed to registry${NC}"
    fi
}

# List images
list_images() {
    echo -e "\n${YELLOW}Built images:${NC}"
    docker images | grep ${IMAGE_PREFIX} | head -20
}

# Main
main() {
    case "${1:-all}" in
        all)
            build_backend
            build_frontend
            push_images
            list_images
            ;;
        backend)
            build_backend
            ;;
        frontend)
            build_frontend
            ;;
        push)
            push_images
            ;;
        list)
            list_images
            ;;
        *)
            echo "Usage: $0 {all|backend|frontend|push|list}"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}=========================================="
    echo "  Build Complete!"
    echo "==========================================${NC}"
}

main "$@"
