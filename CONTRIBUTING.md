# Contributing to SecPipeline

First off, thank you for considering contributing to SecPipeline! 🎉 This project aims to be a comprehensive learning resource for DevSecOps practices, and your contributions help make it better for everyone.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Commit Conventions](#commit-conventions)
- [Adding New Security Tools](#adding-new-security-tools)
- [Adding New Vulnerability Examples](#adding-new-vulnerability-examples)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project follows a standard code of conduct. Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive experience for everyone.

---

## How Can I Contribute?

### 🐛 Bug Reports

- Use the GitHub Issues tab to report bugs
- Include steps to reproduce, expected behavior, and actual behavior
- Add relevant logs or screenshots

### 💡 Feature Requests

- Open an issue with the `enhancement` label
- Describe the feature, its use case, and potential implementation approach

### 🔧 Code Contributions

- Fix bugs or implement features from the issue tracker
- Add new security scanning tools to the pipeline
- Add new vulnerability examples to the demo application
- Improve documentation

### 📚 Documentation

- Fix typos or improve clarity
- Add tutorials or guides
- Translate documentation

---

## Getting Started

### Prerequisites

- Python 3.9+
- Docker 20.10+ & Docker Compose V2
- Git 2.30+

### Fork & Clone

```bash
# 1. Fork the repository on GitHub (click the "Fork" button)

# 2. Clone your fork
git clone https://github.com/<your-username>/secpipeline.git
cd secpipeline

# 3. Add the upstream remote
git remote add upstream https://github.com/NNTung293/secpipeline.git

# 4. Create a feature branch
git checkout -b feat/your-feature-name
```

### Local Development

```bash
# Set up a Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r app/requirements.txt

# Run the app locally
cd app
python app.py

# Or run with Docker Compose
docker compose up --build
```

---

## Development Workflow

1. **Sync with upstream** before starting work:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/add-checkov-scanning
   ```

3. **Make your changes** with clear, atomic commits

4. **Test locally** — ensure the pipeline would pass:
   ```bash
   # Run the app
   docker compose up --build
   
   # Run a local scan (optional)
   docker run --rm -v "${PWD}:/src" returntocorp/semgrep semgrep --config=p/owasp-top-ten /src/app/
   ```

5. **Push and create a Pull Request**:
   ```bash
   git push origin feat/add-checkov-scanning
   ```

---

## Code Style

### Python (PEP 8)

All Python code must follow [PEP 8](https://peps.python.org/pep-0008/):

- **Indentation:** 4 spaces (no tabs)
- **Line length:** Maximum 120 characters
- **Imports:** Group by standard library, third-party, then local — separated by blank lines
- **Naming:**
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
- **Docstrings:** Use triple double-quotes (`"""`) with a brief description

```python
def scan_for_vulnerabilities(target_path: str, severity: str = "HIGH") -> dict:
    """
    Scan the target path for security vulnerabilities.

    Args:
        target_path: Absolute path to the directory to scan.
        severity: Minimum severity level to report.

    Returns:
        Dictionary containing scan results and metadata.
    """
    results = {}
    # ... implementation
    return results
```

### YAML (GitHub Actions)

- **Indentation:** 2 spaces
- **Quoting:** Use quotes for strings that could be misinterpreted
- **Comments:** Add comments explaining non-obvious configuration choices

### Docker

- Use multi-stage builds where applicable
- Pin base image versions (avoid `latest` in production Dockerfiles)
- Order layers from least to most frequently changing

---

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) to maintain a clean and automated changelog.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(pipeline): add Checkov IaC scanning stage` |
| `fix` | Bug fix | `fix(report): correct severity count in dashboard` |
| `docs` | Documentation | `docs(readme): add architecture diagram` |
| `ci` | CI/CD changes | `ci(workflow): pin actions to SHA versions` |
| `refactor` | Code refactoring | `refactor(app): extract database helper functions` |
| `test` | Adding tests | `test(gate): add unit tests for security gate logic` |
| `chore` | Maintenance | `chore(deps): update Trivy to v0.50.0` |
| `style` | Code style | `style(app): fix PEP 8 line length violations` |

### Examples

```bash
# Feature
git commit -m "feat(pipeline): add SBOM generation with Syft"

# Bug fix
git commit -m "fix(zap): handle timeout when app is slow to start"

# Documentation
git commit -m "docs(contributing): add section on adding new tools"

# CI/CD
git commit -m "ci(actions): upgrade checkout action to v4"
```

---

## Adding New Security Tools

Want to integrate a new security tool into the pipeline? Follow these steps:

### 1. Create a New Job in the Workflow

Add a new job in `.github/workflows/security-pipeline.yml`:

```yaml
new-tool-scan:
  name: "🔧 New Tool Scan"
  runs-on: ubuntu-latest
  continue-on-error: true
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run New Tool
      run: |
        # Your scanning command here
    
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: new-tool-results
        path: new-tool-results.json
```

### 2. Update the Report Generator

Modify `scripts/generate_report.py` to parse and include the new tool's output in the HTML dashboard.

### 3. Update Documentation

- Add the tool to the Security Tools table in `README.md`
- Add a Pipeline Stages description
- Update the architecture diagram if necessary

### 4. Test

- Push to a feature branch and verify the pipeline runs successfully
- Check the generated report includes the new tool's findings

---

## Adding New Vulnerability Examples

To add new intentional vulnerabilities to the demo application:

### Guidelines

1. **Map to OWASP** — Each vulnerability should map to an OWASP Top 10 category
2. **Be obvious** — Vulnerabilities should be clearly identifiable by scanning tools
3. **Add comments** — Mark vulnerable code with comments like:
   ```python
   # VULNERABLE: SQL Injection — user input directly concatenated into query
   ```
4. **Update README** — Add the vulnerability to the table in the README
5. **Use fake data** — Never use real credentials, even for demo purposes; use clearly fake values like `FAKE_API_KEY_12345`

### Example

```python
@app.route("/new-vuln")
def new_vulnerability():
    """Demonstrate a new vulnerability type."""
    # VULNERABLE: [Vulnerability Type] — [Brief description]
    user_input = request.args.get("input")
    # ... vulnerable code
    return result
```

---

## Pull Request Process

1. **Ensure your branch is up-to-date** with `main`
2. **Fill out the PR template** with:
   - Description of changes
   - Related issue number (if any)
   - Type of change (feat/fix/docs/ci)
   - Checklist of completed items
3. **Wait for CI checks** — The security pipeline will run on your PR
4. **Address review feedback** promptly
5. **Squash commits** if requested during review

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Commit messages follow Conventional Commits
- [ ] Documentation has been updated (if applicable)
- [ ] New vulnerability examples are mapped to OWASP categories
- [ ] Pipeline runs successfully on the PR branch

---

## 💬 Questions?

If you have questions about contributing, feel free to:

- Open a [GitHub Discussion](https://github.com/NNTung293/secpipeline/discussions)
- Create an issue with the `question` label

Thank you for helping make SecPipeline better! 🛡️
