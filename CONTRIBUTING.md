# Contributing

Thank you for your interest in contributing to the ESC Chatbot!

## How to Contribute

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/your-feature`)
3. **Make your changes**
4. **Run tests** (`pytest tests/ -v`)
5. **Commit** (`git commit -m "feat: add your feature"`)
6. **Push** (`git push origin feature/your-feature`)
7. **Open a Pull Request**

## Development Setup

```bash
git clone https://github.com/esc-software/chatbot
cd chatbot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
```

## Code Style

- Use type hints for all function signatures
- Follow PEP 8 conventions
- Keep functions focused and small
- Write tests for new features

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` a new feature
- `fix:` a bug fix
- `docs:` documentation changes
- `refactor:` code refactoring
- `test:` adding or updating tests
- `chore:` maintenance tasks

## Questions?

Open an issue or reach out at hello@esc-software.com.
