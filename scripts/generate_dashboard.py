#!/usr/bin/env python3
"""
Generate a self-contained HTML dashboard from Guardian JSON data.

Produces a single index.html with embedded CSS — no external dependencies.
Designed to be deployed to GitHub Pages via Actions.

Usage:
    python3 scripts/generate_dashboard.py --prs reports/open-prs.json --output docs/index.html
    python3 scripts/generate_dashboard.py --prs FILE --ci FILE --renovate FILE --sonar FILE -o docs/index.html
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def load_json_safe(path):
    if not path:
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARN: Could not load {path}: {e}", file=sys.stderr)
        return None


def esc(text):
    """Escape HTML entities."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def status_class(status):
    if status in ("OK", "success", "passing", "PASS", "ready_to_merge"):
        return "ok"
    if status in ("ERROR", "failure", "failing", "FAIL", "blocked"):
        return "error"
    if status in ("WARN", "warning", "flaky", "stale", "changes_requested"):
        return "warn"
    if status in ("draft", "NONE", "needs_review"):
        return "neutral"
    return "unknown"


def status_label(status):
    mapping = {
        "OK": "Passing", "ERROR": "Failing", "WARN": "Warning",
        "NONE": "No Gate", "UNKNOWN": "Unknown",
        "success": "Pass", "failure": "Fail",
    }
    return mapping.get(status, status)


def card_html(title, status, detail):
    cls = status_class(status)
    return f'''<div class="card {cls}">
  <div class="card-title">{esc(title)}</div>
  <div class="card-status">{esc(status_label(status))}</div>
  <div class="card-detail">{esc(detail)}</div>
</div>'''


def section_html(section_id, title, count, content, collapsed=False):
    state = "" if not collapsed else ""
    return f'''<details class="section" id="{section_id}" {"" if collapsed else "open"}>
  <summary><h2>{esc(title)} <span class="badge">{count}</span></h2></summary>
  {content}
</details>'''


def build_health_cards(prs_data, ci_data, renovate_data, sonar_data):
    cards = []

    if ci_data:
        agg = ci_data.get("aggregate", ci_data.get("summary", {}))
        failing = agg.get("failing", 0)
        flaky = agg.get("flaky", 0)
        status = "OK" if failing == 0 and flaky == 0 else ("WARN" if failing == 0 else "ERROR")
        cards.append(card_html("CI / Pipeline", status, f"{failing} failing, {flaky} flaky"))
    else:
        cards.append(card_html("CI / Pipeline", "UNKNOWN", "No data"))

    if prs_data:
        agg = prs_data.get("aggregate", prs_data.get("summary", {}))
        ready = agg.get("ready_to_merge", 0)
        stale = agg.get("stale", 0)
        blocked = agg.get("blocked", 0)
        total = agg.get("total_prs", 0)
        status = "OK" if blocked == 0 and stale == 0 else ("WARN" if blocked == 0 else "ERROR")
        cards.append(card_html("Open PRs", status, f"{total} total, {ready} ready, {stale} stale"))
    else:
        cards.append(card_html("Open PRs", "UNKNOWN", "No data"))

    if renovate_data:
        agg = renovate_data.get("aggregate", renovate_data.get("summary", {}))
        overdue = agg.get("overdue", 0)
        security = agg.get("security", 0)
        total = agg.get("total_prs", agg.get("total", 0))
        status = "ERROR" if security > 0 else ("WARN" if overdue > 0 else "OK")
        cards.append(card_html("Dependencies", status, f"{total} open, {overdue} overdue"))
    else:
        cards.append(card_html("Dependencies", "UNKNOWN", "No data"))

    if sonar_data:
        agg = sonar_data.get("aggregate", {})
        gate_fail = agg.get("gate_error", 0)
        vulns = agg.get("total_vulnerabilities", 0)
        gate_ok = agg.get("gate_ok", 0)
        status = "ERROR" if gate_fail > 0 else "OK"
        cards.append(card_html("SonarCloud", status, f"{gate_ok} passing, {gate_fail} failing, {vulns} vulns"))
    else:
        cards.append(card_html("SonarCloud", "UNKNOWN", "No data"))

    return '<div class="cards">' + "\n".join(cards) + "</div>"


def build_ci_section(ci_data):
    if not ci_data:
        return ""

    results = ci_data.get("results", [ci_data])
    failing = []
    flaky = []
    all_repos = []

    for repo in results:
        slug = f"{repo.get('owner', '?')}/{repo.get('repo', '?')}"
        s = repo.get("summary", {})
        repo_status = "ok"
        if repo.get("error"):
            repo_status = "error"
        elif s.get("failing", 0) > 0:
            repo_status = "error"
        elif s.get("flaky", 0) > 0:
            repo_status = "warn"

        all_repos.append(
            f'<tr class="{repo_status}">'
            f"<td>{esc(slug)}</td>"
            f"<td>{s.get('total', 0)}</td>"
            f"<td>{s.get('passing', 0)}</td>"
            f"<td>{s.get('failing', 0)}</td>"
            f"<td>{s.get('flaky', 0)}</td>"
            f'<td><span class="status {repo_status}">{repo_status.upper()}</span></td>'
            f"</tr>"
        )

        for wf in repo.get("workflows", []):
            wf_entry = {"_repo": slug, **wf}
            if wf.get("conclusion") == "failure" and not wf.get("is_flaky"):
                failing.append(wf_entry)
            if wf.get("is_flaky"):
                flaky.append(wf_entry)

    content = ""

    if failing:
        rows = ""
        for wf in failing:
            jobs = ", ".join(j["name"] for j in wf.get("failing_jobs", []))
            url = wf.get("url", "")
            link = f'<a href="{esc(url)}" target="_blank">{esc(wf["name"])}</a>' if url else esc(wf["name"])
            rows += (
                f"<tr>"
                f"<td>{esc(wf['_repo'])}</td>"
                f"<td>{link}</td>"
                f"<td>{wf.get('age_hours', '?')}h</td>"
                f"<td>{esc(jobs or '-')}</td>"
                f"</tr>"
            )
        content += f'''<h3>Failing Workflows ({len(failing)})</h3>
<table><thead><tr><th>Repo</th><th>Workflow</th><th>Age</th><th>Failing Jobs</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    if flaky:
        rows = ""
        for wf in flaky:
            url = wf.get("url", "")
            link = f'<a href="{esc(url)}" target="_blank">{esc(wf["name"])}</a>' if url else esc(wf["name"])
            rows += (
                f"<tr>"
                f"<td>{esc(wf['_repo'])}</td>"
                f"<td>{link}</td>"
                f"<td>{esc(wf.get('conclusion', '?'))}</td>"
                f"</tr>"
            )
        content += f'''<h3>Flaky Workflows ({len(flaky)})</h3>
<table><thead><tr><th>Repo</th><th>Workflow</th><th>Last Result</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    rows = "\n".join(all_repos)
    content += f'''<h3>Per-Repo Status</h3>
<table><thead><tr><th>Repository</th><th>Total</th><th>Passing</th><th>Failing</th><th>Flaky</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    agg = ci_data.get("aggregate", ci_data.get("summary", {}))
    total = agg.get("total_workflows", agg.get("total", 0))
    return section_html("ci", "CI / Pipeline Health", total, content)


def build_pr_section(prs_data):
    if not prs_data:
        return ""

    results = prs_data.get("results", [prs_data])
    categories = [
        ("ready_to_merge", "Ready to Merge", "ok"),
        ("needs_review", "Needs Review", "neutral"),
        ("changes_requested", "Changes Requested", "warn"),
        ("blocked", "Blocked", "error"),
        ("stale", "Stale", "warn"),
        ("draft", "Draft", "neutral"),
    ]

    prs_by_cat = {k: [] for k, _, _ in categories}
    for repo in results:
        slug = f"{repo.get('owner', '?')}/{repo.get('repo', '?')}"
        if repo.get("error"):
            continue
        for pr in repo.get("prs", []):
            pr["_repo"] = slug
            cat = pr.get("category", "needs_review")
            if cat in prs_by_cat:
                prs_by_cat[cat].append(pr)

    content = ""
    for cat_key, cat_title, cls in categories:
        prs = prs_by_cat[cat_key]
        if not prs:
            continue

        prs.sort(key=lambda p: p.get("age_days", 0), reverse=True)
        rows = ""
        for pr in prs:
            url = pr.get("url", "")
            link = f'<a href="{esc(url)}" target="_blank">#{pr["number"]}</a>' if url else f'#{pr["number"]}'
            rows += (
                f"<tr>"
                f"<td>{esc(pr['_repo'])}</td>"
                f"<td>{link}</td>"
                f"<td>{esc(pr.get('title', '')[:60])}</td>"
                f"<td>{esc(pr.get('author', ''))}</td>"
                f"<td>{pr.get('age_days', 0)}d</td>"
                f"</tr>"
            )
        content += f'''<h3><span class="status {cls}">{cat_title}</span> ({len(prs)})</h3>
<table><thead><tr><th>Repo</th><th>PR</th><th>Title</th><th>Author</th><th>Age</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    agg = prs_data.get("aggregate", prs_data.get("summary", {}))
    total = agg.get("total_prs", 0)
    return section_html("prs", "Open Pull Requests", total, content)


def build_renovate_section(renovate_data):
    if not renovate_data:
        return ""

    results = renovate_data.get("results", [renovate_data])
    priority_order = {"security": 0, "major": 1, "minor": 2}
    overdue = []
    pending = []

    for repo in results:
        slug = f"{repo.get('owner', '?')}/{repo.get('repo', '?')}"
        if repo.get("error"):
            continue
        for pr in repo.get("prs", []):
            pr["_repo"] = slug
            if pr.get("is_overdue"):
                overdue.append(pr)
            else:
                pending.append(pr)

    content = ""

    if overdue:
        overdue.sort(key=lambda p: (priority_order.get(p.get("update_type", "minor"), 2), -p.get("age_days", 0)))
        rows = ""
        for pr in overdue:
            url = pr.get("url", "")
            link = f'<a href="{esc(url)}" target="_blank">#{pr["number"]}</a>' if url else f'#{pr["number"]}'
            utype = pr.get("update_type", "?")
            cls = "error" if utype == "security" else "warn"
            rows += (
                f"<tr>"
                f"<td>{esc(pr['_repo'])}</td>"
                f"<td>{link}</td>"
                f"<td>{esc(pr.get('title', '')[:50])}</td>"
                f'<td><span class="status {cls}">{esc(utype)}</span></td>'
                f"<td>{pr.get('age_days', 0)}d</td>"
                f"<td>{pr.get('threshold_days', '?')}d</td>"
                f"</tr>"
            )
        content += f'''<h3>Overdue ({len(overdue)})</h3>
<table><thead><tr><th>Repo</th><th>PR</th><th>Title</th><th>Type</th><th>Age</th><th>Threshold</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    if pending:
        pending.sort(key=lambda p: p.get("age_days", 0), reverse=True)
        rows = ""
        for pr in pending:
            url = pr.get("url", "")
            link = f'<a href="{esc(url)}" target="_blank">#{pr["number"]}</a>' if url else f'#{pr["number"]}'
            rows += (
                f"<tr>"
                f"<td>{esc(pr['_repo'])}</td>"
                f"<td>{link}</td>"
                f"<td>{esc(pr.get('title', '')[:50])}</td>"
                f"<td>{esc(pr.get('update_type', '?'))}</td>"
                f"<td>{pr.get('age_days', 0)}d</td>"
                f"</tr>"
            )
        content += f'''<h3>Pending ({len(pending)})</h3>
<table><thead><tr><th>Repo</th><th>PR</th><th>Title</th><th>Type</th><th>Age</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    agg = renovate_data.get("aggregate", renovate_data.get("summary", {}))
    total = agg.get("total_prs", agg.get("total", 0))
    return section_html("deps", "Dependency Updates", total, content, collapsed=True)


def build_sonar_section(sonar_data):
    if not sonar_data:
        return ""

    results = sonar_data.get("results", [sonar_data])

    rows = ""
    for proj in results:
        slug = f"{proj.get('owner', '?')}/{proj.get('repo', '?')}"
        m = proj.get("metrics", {})
        gate = proj.get("gate_status", "UNKNOWN")
        cls = status_class(gate)

        if proj.get("error"):
            rows += f'<tr class="error"><td>{esc(slug)}</td><td colspan="7">Error fetching data</td></tr>'
            continue

        coverage = m.get("coverage", "N/A")
        if isinstance(coverage, (int, float)):
            cov_cls = "ok" if coverage >= 80 else ("warn" if coverage >= 50 else "error")
            coverage_str = f'<span class="status {cov_cls}">{coverage}%</span>'
        else:
            coverage_str = "N/A"

        rows += (
            f'<tr class="{cls}">'
            f"<td>{esc(slug)}</td>"
            f'<td><span class="status {cls}">{esc(status_label(gate))}</span></td>'
            f"<td>{coverage_str}</td>"
            f"<td>{m.get('bugs', 'N/A')}</td>"
            f"<td>{m.get('vulnerabilities', 'N/A')}</td>"
            f"<td>{m.get('code_smells', 'N/A')}</td>"
            f"<td>{m.get('security_hotspots', 'N/A')}</td>"
            f"<td>{m.get('security_rating', 'N/A')}</td>"
            f"</tr>"
        )

    content = f'''<table>
<thead><tr><th>Repository</th><th>Gate</th><th>Coverage</th><th>Bugs</th><th>Vulns</th><th>Smells</th><th>Hotspots</th><th>Security</th></tr></thead>
<tbody>{rows}</tbody>
</table>'''

    failing = [r for r in results if r.get("gate_status") == "ERROR"]
    if failing:
        details = ""
        for proj in failing:
            slug = f"{proj.get('owner', '?')}/{proj.get('repo', '?')}"
            fail_conds = proj.get("failing_conditions", [])
            reasons = ", ".join(c["metric"] + "=" + str(c["value"]) for c in fail_conds[:3])
            details += f"<li><strong>{esc(slug)}</strong> — {esc(reasons)}</li>"
        content = f"<h3>Failing Gates ({len(failing)})</h3><ul>{details}</ul>" + content

    total = sonar_data.get("total_projects", len(results))
    return section_html("sonar", "SonarCloud Quality", total, content, collapsed=True)


CSS = """
:root {
  --bg: #0d1117; --surface: #161b22; --border: #30363d;
  --text: #e6edf3; --text-muted: #8b949e;
  --ok: #238636; --ok-bg: #0d2117; --ok-text: #3fb950;
  --warn: #9e6a03; --warn-bg: #2a1e00; --warn-text: #d29922;
  --error: #da3633; --error-bg: #2d0a0a; --error-text: #f85149;
  --neutral: #30363d; --neutral-text: #8b949e;
  --link: #58a6ff;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.5; padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
.subtitle { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }

.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem;
        border-left: 4px solid var(--neutral); }
.card.ok { border-left-color: var(--ok); background: var(--ok-bg); }
.card.error { border-left-color: var(--error); background: var(--error-bg); }
.card.warn { border-left-color: var(--warn); background: var(--warn-bg); }
.card-title { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.card-status { font-size: 1.4rem; font-weight: 600; margin: 0.25rem 0; }
.card.ok .card-status { color: var(--ok-text); }
.card.error .card-status { color: var(--error-text); }
.card.warn .card-status { color: var(--warn-text); }
.card-detail { font-size: 0.85rem; color: var(--text-muted); }

.section { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
           margin-bottom: 1rem; }
.section summary { cursor: pointer; padding: 0.75rem 1rem; list-style: none; }
.section summary::-webkit-details-marker { display: none; }
.section summary::before { content: '▶ '; font-size: 0.7rem; color: var(--text-muted); }
.section[open] summary::before { content: '▼ '; }
.section summary h2 { display: inline; font-size: 1.1rem; }
.section > :not(summary) { padding: 0 1rem 1rem; }
.badge { background: var(--border); color: var(--text-muted); font-size: 0.75rem; font-weight: normal;
         padding: 0.15em 0.5em; border-radius: 10px; vertical-align: middle; }
h3 { font-size: 0.95rem; margin: 1rem 0 0.5rem; }

table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-bottom: 1rem; }
th { text-align: left; padding: 0.5rem; border-bottom: 2px solid var(--border); color: var(--text-muted);
     font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
td { padding: 0.5rem; border-bottom: 1px solid var(--border); }
tr:hover { background: rgba(255,255,255,0.03); }

.status { display: inline-block; padding: 0.1em 0.5em; border-radius: 4px; font-size: 0.8rem; font-weight: 500; }
.status.ok { background: var(--ok-bg); color: var(--ok-text); border: 1px solid var(--ok); }
.status.error { background: var(--error-bg); color: var(--error-text); border: 1px solid var(--error); }
.status.warn { background: var(--warn-bg); color: var(--warn-text); border: 1px solid var(--warn); }
.status.neutral { background: var(--surface); color: var(--neutral-text); border: 1px solid var(--neutral); }

ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
li { margin-bottom: 0.3rem; font-size: 0.9rem; }

@media (max-width: 600px) {
  body { padding: 0.75rem; }
  .cards { grid-template-columns: 1fr 1fr; }
  table { font-size: 0.75rem; }
  td, th { padding: 0.35rem; }
}
"""


def generate_dashboard(prs_data, ci_data, renovate_data, sonar_data):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    health_cards = build_health_cards(prs_data, ci_data, renovate_data, sonar_data)
    ci_section = build_ci_section(ci_data)
    pr_section = build_pr_section(prs_data)
    renovate_section = build_renovate_section(renovate_data)
    sonar_section = build_sonar_section(sonar_data)

    sections = "\n".join(s for s in [ci_section, pr_section, renovate_section, sonar_section] if s)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guardian Dashboard — Ansible Devtools</title>
<style>{CSS}</style>
</head>
<body>
<h1>Guardian Dashboard</h1>
<p class="subtitle">Ansible Devtools — Last updated: {esc(now_str)}</p>

{health_cards}

{sections}

<p class="subtitle" style="margin-top:2rem; text-align:center;">
  Generated by devtools-guardian
</p>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate Guardian HTML dashboard")
    parser.add_argument("--prs", help="PR data JSON file")
    parser.add_argument("--ci", help="CI status JSON file")
    parser.add_argument("--renovate", help="Renovate/dependency PR JSON file")
    parser.add_argument("--sonar", help="SonarCloud quality gate JSON file")
    parser.add_argument("--output", "-o", default="docs/index.html",
                        help="Output HTML file (default: docs/index.html)")
    args = parser.parse_args()

    prs_data = load_json_safe(args.prs)
    ci_data = load_json_safe(args.ci)
    renovate_data = load_json_safe(args.renovate)
    sonar_data = load_json_safe(args.sonar)

    if not any([prs_data, ci_data, renovate_data, sonar_data]):
        print("ERROR: No data files provided or loadable", file=sys.stderr)
        sys.exit(1)

    html = generate_dashboard(prs_data, ci_data, renovate_data, sonar_data)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)

    print(f"Dashboard written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
