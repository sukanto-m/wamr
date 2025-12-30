# Quick Start Guide

Get WhoAteMyRAM running in 5 minutes.

## Prerequisites

You need:
1. Linux system
2. Python 3.8+
3. Internet connection (for initial setup)

## Step 1: Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

This installs Ollama, the local LLM runtime.

## Step 2: Pull a Model

```bash
ollama pull llama3.2:3b
```

This downloads a 3B parameter model (~2GB). Takes 2-5 minutes depending on your internet.

## Step 3: Start Ollama

```bash
ollama serve
```

Keep this terminal open, or run in background:

```bash
nohup ollama serve > /dev/null 2>&1 &
```

## Step 4: Install WhoAteMyRAM

```bash
# Clone the repo
git clone https://github.com/yourusername/whoatemyram.git
cd whoatemyram

# Run installer
./install.sh
```

The installer will:
- Check dependencies
- Install Python requirements
- Copy `wamr` to `/usr/local/bin`
- Verify everything works

## Step 5: Run It!

```bash
# Try the demo first (no Ollama needed)
wamr --demo

# Or run with real system analysis
wamr
```

That's it! You should see an analysis of your system memory.

---

## Troubleshooting

### "Cannot connect to Ollama"

Make sure Ollama is running:

```bash
# Check if running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "Model not found"

Pull the model:

```bash
ollama pull llama3.2:3b
```

### "Permission denied"

The installer needs sudo for system-wide install:

```bash
sudo ./install.sh
```

Or install locally:

```bash
# Copy to your local bin
mkdir -p ~/.local/bin
cp wamr.py ~/.local/bin/wamr
chmod +x ~/.local/bin/wamr

# Add to PATH (add this to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Python dependencies issues

Install manually:

```bash
pip install --user requests
```

---

## What's Next?

Try these commands:

```bash
# Quick check without LLM
wamr --no-llm

# Use a different model
wamr --model llama3.1:8b

# Get JSON output
wamr --json

# See all options
wamr --help
```

Read [EXAMPLES.md](EXAMPLES.md) for more usage scenarios.

---

## Uninstall

```bash
# Remove the binary
sudo rm /usr/local/bin/wamr

# Optionally remove Ollama
curl -fsSL https://ollama.ai/uninstall.sh | sh

# Remove the repo
cd .. && rm -rf whoatemyram
```

---

## Performance Notes

### Model Speed Comparison

On a typical laptop (no GPU):

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.2:1b | 1GB | ~2-3 sec | Good |
| llama3.2:3b | 2GB | ~5-8 sec | Better |
| llama3.1:8b | 4.7GB | ~15-30 sec | Best |

With GPU (NVIDIA):
- All models run 5-10x faster
- 8B model runs in ~3-5 seconds

### Recommendation

- **No GPU**: Use llama3.2:1b or 3b
- **With GPU**: Use llama3.1:8b for best results

---

## Getting Help

1. Check [EXAMPLES.md](EXAMPLES.md)
2. Check [README.md](README.md)
3. Open an issue on GitHub
4. Read the [Contributing Guide](CONTRIBUTING.md)

Happy memory hunting! 💾✨
