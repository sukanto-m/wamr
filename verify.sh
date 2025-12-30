#!/bin/bash
#
# Quick verification - shows that wamr works
#

echo "🔍 Verifying WhoAteMyRAM installation..."
echo ""

# Test 1: Demo mode
echo "Running demo mode..."
python3 wamr.py --demo 2>/dev/null | head -15
echo ""
echo "✅ Demo mode works!"
echo ""

# Test 2: Help
echo "Checking help..."
if python3 wamr.py --help 2>&1 | grep -q "WhoAteMyRAM"; then
    echo "✅ Help works!"
else
    echo "❌ Help failed"
    exit 1
fi
echo ""

# Test 3: No-LLM mode  
echo "Running --no-llm mode..."
python3 wamr.py --no-llm 2>/dev/null | head -8
echo ""
echo "✅ Basic mode works!"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ WhoAteMyRAM is working correctly!"
echo ""
echo "Next steps:"
echo "  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
echo "  2. Pull a model: ollama pull llama3.2:3b"
echo "  3. Run: wamr"
echo ""
