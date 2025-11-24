#!/bin/bash
# Docker configuration validation script

set -e

echo "========================================="
echo "Docker Configuration Validation"
echo "========================================="
echo ""

# Check if Docker is installed
echo "1. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker version: $(docker --version)"
echo ""

# Check if docker-compose is installed
echo "2. Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose version: $(docker-compose --version)"
echo ""

# Validate Dockerfile syntax
echo "3. Validating Dockerfile..."
if [ ! -f "docker/Dockerfile" ]; then
    echo "❌ docker/Dockerfile not found"
    exit 1
fi
echo "✅ docker/Dockerfile exists"
echo ""

# Validate docker-compose.yml syntax
echo "4. Validating docker-compose.yml..."
if [ ! -f "docker/docker-compose.yml" ]; then
    echo "❌ docker/docker-compose.yml not found"
    exit 1
fi

cd docker
docker-compose config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ docker-compose.yml syntax is valid"
else
    echo "❌ docker-compose.yml has syntax errors"
    exit 1
fi
cd ..
echo ""

# Check entrypoint script
echo "5. Checking entrypoint script..."
if [ ! -f "docker/docker-entrypoint.sh" ]; then
    echo "❌ docker/docker-entrypoint.sh not found"
    exit 1
fi

if [ ! -x "docker/docker-entrypoint.sh" ]; then
    echo "⚠️  docker-entrypoint.sh is not executable, fixing..."
    chmod +x docker/docker-entrypoint.sh
fi
echo "✅ docker-entrypoint.sh is ready"
echo ""

# Check .dockerignore
echo "6. Checking .dockerignore..."
if [ ! -f "docker/.dockerignore" ]; then
    echo "⚠️  docker/.dockerignore not found (optional)"
else
    echo "✅ docker/.dockerignore exists"
fi
echo ""

# Check required directories
echo "7. Checking required directories..."
for dir in data logs configs; do
    if [ ! -d "$dir" ]; then
        echo "⚠️  Directory $dir does not exist, creating..."
        mkdir -p "$dir"
    fi
    echo "✅ Directory $dir exists"
done
echo ""

# Check requirements.txt
echo "8. Checking requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi
echo "✅ requirements.txt exists"
echo ""

echo "========================================="
echo "✅ All validations passed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Enter docker directory: cd docker"
echo "2. Build the image: docker-compose build"
echo "3. Start services: docker-compose up -d"
echo "4. View logs: docker-compose logs -f"
echo ""
echo "Note: First build will take 5-10 minutes due to TA-Lib compilation"
