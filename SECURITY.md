# Security Policy

## ⚠️ Important Notice

This repository contains an **intentionally vulnerable** web application designed for educational and demonstration purposes. The vulnerabilities present in the Flask application (`app/`) are **deliberate** and serve to showcase the capabilities of the integrated security scanning tools.

**DO NOT** deploy this application in any production, staging, or publicly accessible environment.

---

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | ✅ Current release  |
| < 1.0   | ❌ Not supported    |

---

## Scope

### ❌ Out of Scope (Intentionally Vulnerable)

The following components are **intentionally vulnerable** and are **not** eligible for vulnerability reports:

- The Flask web application (`app/` directory)
- Sample infrastructure files (`sample-infra/` directory)
- Hardcoded credentials in source code (demonstration purposes)
- Known vulnerable dependencies in `requirements.txt`

### ✅ In Scope

We **do** accept security reports for vulnerabilities found in:

- **Pipeline configuration** — Issues in GitHub Actions workflows (`.github/workflows/`)
- **Scanning scripts** — Bugs in the report generation or security gate logic (`scripts/`)
- **CI/CD security** — Misconfigurations that could lead to pipeline compromise (e.g., secret exposure, command injection in workflow files)
- **Repository security** — Issues with repository settings, permissions, or access controls

---

## Reporting a Vulnerability

If you discover a security issue **within scope** (pipeline configuration, scanning scripts, or CI/CD security), please follow these steps:

1. **Open a GitHub Issue** — Create an issue with the label `security` describing the vulnerability
2. **Include details** — Provide as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested remediation (if any)
3. **Response time** — We aim to acknowledge reports within **72 hours** and provide a fix or mitigation plan within **7 days**

> **Note:** Since this is an educational project, we use public issues rather than private disclosure. If you believe the issue is sensitive enough to warrant private disclosure, please contact the repository owner directly.

---

## Security Best Practices for Contributors

When contributing to this project, please ensure:

- ✅ **No real secrets** — Never commit actual API keys, passwords, or tokens (use clearly fake/demo values)
- ✅ **Scoped permissions** — GitHub Actions workflows should use least-privilege permissions
- ✅ **Pinned actions** — Use SHA-pinned versions for third-party GitHub Actions
- ✅ **Input validation** — Sanitize inputs in pipeline scripts to prevent injection attacks
- ✅ **Review workflows** — All changes to `.github/workflows/` require careful review

---

## Acknowledgments

We appreciate the security community's efforts in keeping open-source projects safe. Thank you for respecting the scope of this educational project.
