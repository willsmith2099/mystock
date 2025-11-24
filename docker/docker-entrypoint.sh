#!/bin/bash
# Docker entrypoint script for Stock Prediction System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Stock Prediction System${NC}"
echo -e "${GREEN}========================================${NC}"

# Initialize directories
echo -e "${YELLOW}Initializing directories...${NC}"
mkdir -p /app/data/raw /app/data/processed /app/data/models /app/logs

# Check if data directories are writable
if [ ! -w /app/data ]; then
    echo -e "${RED}Error: /app/data is not writable${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Directories initialized${NC}"

# Run based on command argument
case "$1" in
    api)
        echo -e "${YELLOW}Starting FastAPI server...${NC}"
        exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    
    worker)
        echo -e "${YELLOW}Starting background worker...${NC}"
        exec python -m src.worker.main
        ;;
    
    test)
        echo -e "${YELLOW}Running tests...${NC}"
        exec python scripts/test_system.py
        ;;
    
    demo)
        echo -e "${YELLOW}Running quick demo...${NC}"
        exec python scripts/quick_start.py
        ;;
    
    predict)
        echo -e "${YELLOW}Running stock prediction...${NC}"
        shift  # Remove 'predict' from arguments
        exec python scripts/predict_stock.py "$@"
        ;;
    
    bash)
        echo -e "${YELLOW}Starting interactive bash shell...${NC}"
        exec /bin/bash
        ;;
    
    *)
        echo -e "${YELLOW}Running custom command: $@${NC}"
        exec "$@"
        ;;
esac
