#!/bin/bash
#
# WhoAteMyRAM Installation Script
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="wamr"

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   WhoAteMyRAM Installation Script     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This tool currently only supports Linux${NC}"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check for Ollama
echo ""
echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} Ollama not found"
    echo ""
    echo "WhoAteMyRAM requires Ollama to run."
    echo "Install it with:"
    echo ""
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    read -p "Continue installation anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Ollama found"
    
    # Check if ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama is running"
        
        # Check for llama3.2:3b model
        if ollama list | grep -q "llama3.2:3b"; then
            echo -e "${GREEN}✓${NC} llama3.2:3b model found"
        else
            echo -e "${YELLOW}⚠${NC} llama3.2:3b model not found"
            echo ""
            echo "Recommended: Install the default model with:"
            echo "  ollama pull llama3.2:3b"
            echo ""
        fi
    else
        echo -e "${YELLOW}⚠${NC} Ollama is not running"
        echo ""
        echo "Start it with: ollama serve"
        echo ""
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if python3 -m pip install --user requests &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Could not install requests library"
    echo "Install manually with: pip install requests"
fi

# Install the script
echo ""
echo "Installing wamr to $INSTALL_DIR..."

if [ -w "$INSTALL_DIR" ]; then
    # Can write directly
    cp wamr.py "$INSTALL_DIR/$SCRIPT_NAME"
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    echo -e "${GREEN}✓${NC} Installed to $INSTALL_DIR/$SCRIPT_NAME"
else
    # Need sudo
    echo "Need sudo privileges to install to $INSTALL_DIR"
    sudo cp wamr.py "$INSTALL_DIR/$SCRIPT_NAME"
    sudo chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    echo -e "${GREEN}✓${NC} Installed to $INSTALL_DIR/$SCRIPT_NAME"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation Complete! 🎉          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Try it out:"
echo "  wamr               # Full LLM analysis"
echo "  wamr --no-llm      # Quick process list"
echo "  wamr --help        # See all options"
echo ""
echo "If Ollama is not running, start it with:"
echo "  ollama serve"
echo ""
