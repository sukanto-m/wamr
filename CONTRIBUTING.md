# Contributing to WhoAteMyRAM

Thank you for your interest in contributing! This project was built as a 24-hour hackathon proof-of-concept, but we welcome improvements and extensions.

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit** (`git commit -m 'Add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/whoatemyram.git
cd whoatemyram

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 wamr.py --no-llm  # Basic test
python3 demo.py            # Demo mode
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

## Testing

Before submitting a PR:

1. Test with `--no-llm` flag (should always work)
2. Test with actual Ollama if possible
3. Test on a clean Linux system
4. Verify output formatting looks good

## Ideas for Contributions

### High Priority
- [ ] macOS support (use `vm_stat` instead of `/proc/meminfo`)
- [ ] Memory tracking over time (detect leaks)
- [ ] Interactive kill confirmation mode
- [ ] Better error handling for edge cases

### Medium Priority
- [ ] Container-specific analysis (Docker/Podman insights)
- [ ] Historical comparison mode
- [ ] Custom rules/plugins system
- [ ] Config file support (~/.wamrrc)

### Nice to Have
- [ ] Daemon/monitoring mode
- [ ] Web dashboard
- [ ] Integration with other tools (htop, glances)
- [ ] Support for more LLM backends (LocalAI, llama.cpp)

## Bug Reports

Please include:
- Operating system and version
- Python version
- Ollama version
- Model being used
- Full error message
- Steps to reproduce

## Feature Requests

Open an issue with:
- Clear description of the feature
- Use case / motivation
- Example of expected behavior
- Any relevant mockups or examples

## Questions?

Feel free to open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
