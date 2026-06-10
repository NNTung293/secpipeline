#!/usr/bin/env python3
"""
SecPipeline Security Report Generator
Aggregates scan results from multiple security tools and generates an HTML report.
"""

import json
import os
import sys
from datetime import datetime, timezone

try:
    from jinja2 import Template
except ImportError:
    print("ERROR: jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)


RESULTS_DIR = "scan-results"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "report_template.html")
OUTPUT_PATH = "security-report.html"

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4, "UNKNOWN": 5}


def normalize_severity(sev):
    """Normalize severity strings to a standard set."""
    if not sev:
        return "INFO"
    sev = sev.upper().strip()
    mapping = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "MED": "MEDIUM",
        "LOW": "LOW",
        "INFO": "INFO",
        "INFORMATIONAL": "INFO",
        "NOTE": "INFO",
        "WARNING": "MEDIUM",
        "ERROR": "HIGH",
    }
    return mapping.get(sev, "INFO")


def parse_semgrep(filepath):
    """Parse Semgrep JSON results."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("results", [])
        for r in results:
            severity = r.get("extra", {}).get("severity", "INFO")
            findings.append({
                "tool": "Semgrep",
                "severity": normalize_severity(severity),
                "title": r.get("check_id", "Unknown Rule"),
                "description": r.get("extra", {}).get("message", "No description"),
                "file": r.get("path", "N/A"),
                "line": r.get("start", {}).get("line", "N/A"),
            })
    except FileNotFoundError:
        print(f"  [SKIP] Semgrep results not found: {filepath}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] Error parsing Semgrep results: {e}")
    return findings


def parse_bandit(filepath):
    """Parse Bandit JSON results."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("results", [])
        for r in results:
            severity = r.get("issue_severity", "LOW")
            findings.append({
                "tool": "Bandit",
                "severity": normalize_severity(severity),
                "title": f"{r.get('test_id', 'N/A')}: {r.get('test_name', 'Unknown')}",
                "description": r.get("issue_text", "No description"),
                "file": r.get("filename", "N/A"),
                "line": r.get("line_number", "N/A"),
            })
    except FileNotFoundError:
        print(f"  [SKIP] Bandit results not found: {filepath}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] Error parsing Bandit results: {e}")
    return findings


def parse_trivy(filepath):
    """Parse Trivy JSON results."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("Results", [])
        for result in results:
            target = result.get("Target", "N/A")
            vulns = result.get("Vulnerabilities", [])
            if vulns is None:
                continue
            for v in vulns:
                severity = v.get("Severity", "UNKNOWN")
                findings.append({
                    "tool": "Trivy",
                    "severity": normalize_severity(severity),
                    "title": f"{v.get('VulnerabilityID', 'N/A')}: {v.get('PkgName', 'Unknown')}",
                    "description": v.get("Title", v.get("Description", "No description"))[:200],
                    "file": target,
                    "line": "N/A",
                })
    except FileNotFoundError:
        print(f"  [SKIP] Trivy results not found: {filepath}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] Error parsing Trivy results: {e}")
    return findings


def parse_pip_audit(filepath):
    """Parse pip-audit JSON results."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        dependencies = data.get("dependencies", [])
        for dep in dependencies:
            vulns = dep.get("vulns", [])
            for v in vulns:
                findings.append({
                    "tool": "pip-audit",
                    "severity": normalize_severity(v.get("fix_versions", ["HIGH"])[0] if False else "HIGH"),
                    "title": f"{v.get('id', 'N/A')}: {dep.get('name', 'Unknown')} {dep.get('version', '')}",
                    "description": v.get("description", "No description")[:200],
                    "file": "requirements.txt",
                    "line": "N/A",
                })
    except FileNotFoundError:
        print(f"  [SKIP] pip-audit results not found: {filepath}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] Error parsing pip-audit results: {e}")
    return findings


def parse_zap(filepath):
    """Parse OWASP ZAP JSON results."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        sites = data.get("site", [])
        if isinstance(sites, dict):
            sites = [sites]
        for site in sites:
            alerts = site.get("alerts", [])
            for alert in alerts:
                risk_map = {"0": "INFO", "1": "LOW", "2": "MEDIUM", "3": "HIGH"}
                risk = risk_map.get(str(alert.get("riskcode", "0")), "INFO")
                findings.append({
                    "tool": "ZAP",
                    "severity": normalize_severity(risk),
                    "title": alert.get("alert", alert.get("name", "Unknown")),
                    "description": alert.get("desc", "No description")[:200],
                    "file": alert.get("url", "N/A"),
                    "line": "N/A",
                })
    except FileNotFoundError:
        print(f"  [SKIP] ZAP results not found: {filepath}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] Error parsing ZAP results: {e}")
    return findings


def find_and_parse_results(results_dir):
    """Walk through scan-results directory and parse all JSON files."""
    all_findings = []

    if not os.path.exists(results_dir):
        print(f"WARNING: Results directory '{results_dir}' not found.")
        return all_findings

    # Map filenames to parser functions
    parsers = {
        "semgrep-results.json": parse_semgrep,
        "bandit-results.json": parse_bandit,
        "trivy-sca-results.json": parse_trivy,
        "trivy-image-results.json": parse_trivy,
        "pip-audit-results.json": parse_pip_audit,
        "report_json.json": parse_zap,
    }

    for root, dirs, files in os.walk(results_dir):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                parser = parsers.get(filename)
                if parser:
                    print(f"  Parsing {filepath} with {parser.__name__}...")
                    findings = parser(filepath)
                    all_findings.extend(findings)
                    print(f"    Found {len(findings)} findings")
                else:
                    print(f"  [SKIP] No parser for: {filename}")

    return all_findings


def calculate_stats(findings):
    """Calculate summary statistics."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    tool_counts = {}

    for f in findings:
        sev = f.get("severity", "INFO")
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["INFO"] += 1

        tool = f.get("tool", "Unknown")
        tool_counts[tool] = tool_counts.get(tool, 0) + 1

    return severity_counts, tool_counts


def generate_report(findings, severity_counts, tool_counts):
    """Generate HTML report using Jinja2 template."""
    scan_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(findings)
    gate_status = "FAILED" if severity_counts.get("CRITICAL", 0) > 0 else "PASSED"

    # Sort findings by severity
    findings.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "INFO"), 5))

    # Prepare chart data
    severity_data = json.dumps({
        "labels": ["Critical", "High", "Medium", "Low", "Info"],
        "values": [
            severity_counts.get("CRITICAL", 0),
            severity_counts.get("HIGH", 0),
            severity_counts.get("MEDIUM", 0),
            severity_counts.get("LOW", 0),
            severity_counts.get("INFO", 0),
        ],
        "colors": ["#f85149", "#f0883e", "#d29922", "#58a6ff", "#8b949e"],
    })

    # Load template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"ERROR: Template not found at {TEMPLATE_PATH}")
        sys.exit(1)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_str = f.read()

    template = Template(template_str)
    html = template.render(
        scan_date=scan_date,
        total_findings=total,
        critical_count=severity_counts.get("CRITICAL", 0),
        high_count=severity_counts.get("HIGH", 0),
        medium_count=severity_counts.get("MEDIUM", 0),
        low_count=severity_counts.get("LOW", 0),
        info_count=severity_counts.get("INFO", 0),
        gate_status=gate_status,
        findings=findings,
        tool_stats=tool_counts,
        severity_data=severity_data,
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Report generated: {OUTPUT_PATH}")
    return gate_status


def main():
    print("=" * 60)
    print("🛡️  SecPipeline - Security Report Generator")
    print("=" * 60)

    print(f"\n📂 Scanning results directory: {RESULTS_DIR}")
    findings = find_and_parse_results(RESULTS_DIR)

    print(f"\n📊 Calculating statistics...")
    severity_counts, tool_counts = calculate_stats(findings)

    print(f"\n📝 Generating HTML report...")
    gate_status = generate_report(findings, severity_counts, tool_counts)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SECURITY SCAN SUMMARY")
    print("=" * 60)
    print(f"  Total Findings: {len(findings)}")
    print(f"  🔴 Critical:    {severity_counts.get('CRITICAL', 0)}")
    print(f"  🟠 High:        {severity_counts.get('HIGH', 0)}")
    print(f"  🟡 Medium:      {severity_counts.get('MEDIUM', 0)}")
    print(f"  🔵 Low:         {severity_counts.get('LOW', 0)}")
    print(f"  ⚪ Info:         {severity_counts.get('INFO', 0)}")
    print()
    print("  Findings by Tool:")
    for tool, count in sorted(tool_counts.items()):
        print(f"    {tool}: {count}")
    print()
    print(f"  🔒 Security Gate: {gate_status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
