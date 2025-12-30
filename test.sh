#!/bin/bash
#
# WhoAteMyRAM Test Script
# Verifies that everything is working correctly
#

set -e

echo "🧪 WhoAteMyRAM Test Suite"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test 1: Check Python
echo -n "Test 1: Python 3 available... "
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 2: Check wamr.py exists
echo -n "Test 2: wamr.py exists... "
if [ -f "wamr.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 3: wamr.py is executable
echo -n "Test 3: wamr.py is executable... "
if [ -x "wamr.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 4: Can import Python modules
echo -n "Test 4: Python dependencies available... "
if python3 -c "import sys, subprocess, json, time, os" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 5: --help flag works
echo -n "Test 5: --help flag works... "
if python3 wamr.py --help &> /dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 6: --no-llm mode works
echo -n "Test 6: --no-llm mode works... "
TEST6_OUTPUT=$(python3 wamr.py --no-llm 2>&1)
if echo "$TEST6_OUTPUT" | grep -q "Memory:"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Output was:"
    echo "$TEST6_OUTPUT" | head -5 | sed 's/^/    /'
    FAILED=$((FAILED + 1))
fi

# Test 7: Demo script works
echo -n "Test 7: demo.py works... "
if [ -f "demo.py" ] && python3 demo.py 2>&1 | grep -q "WhoAteMyRAM"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 8: Check Ollama (optional)
echo -n "Test 8: Ollama available (optional)... "
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
    
    # Bonus: Check if Ollama is running
    echo -n "  ↳ Ollama service running... "
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} (not required for basic tests)"
fi

# Summary
echo ""
echo "=========================="
echo "Test Results:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    echo ""
    echo "You can now run:"
    echo "  ./wamr.py --no-llm    # Quick test"
    echo "  ./demo.py             # See demo output"
    echo "  ./install.sh          # Install system-wide"
    exit 0
else
    echo -e "${RED}Some tests failed. Please fix issues above.${NC}"
    exit 1
fi
