"""
Fetch GitHub Actions workflow status across Ansible Devtools repositories.

Reports the latest run status for each workflow on the default branch,
identifies failing jobs, and detects flaky workflows (alternating pass/fail).

Usage:
    python3 scripts/fetch_ci_status.py ansible ansible-lint
    python3 scripts/fetch_ci_status.py --repos-file config/repos.json
    python3 scripts/fetch_ci_status.py --repos-file config/repos.json --days 3
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta


FLAKY_WINDOW = 5


def gh_api(endpoint):
    """Call gh api and return parsed JSON. Returns None on failure."""
    cmd = ["gh", "api", endpoint]
    print(f"  gh api {endpoint[:80]}...", file=sys.stderr)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        print("ERROR: gh CLI not found", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {endpoint}", file=sys.stderr)
        return None

    if result.returncode != 0:
        stderr_msg = result.stderr.strip()
        print(f"  WARN: {endpoint} -> {stderr_msg[:100]}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def detect_flaky(owner, repo, workflow_id, branch):
    """Check last N runs of a workflow to detect flaky behavior."""
    data = gh_api(
        f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        f"?branch={branch}&per_page={FLAKY_WINDOW}&status=completed"
    )
    if not data or "workflow_runs" not in data:
        return False

    conclusions = [r.get("conclusion", "") for r in data["workflow_runs"]]
    if len(conclusions) < 3:
        return False

    alternations = 0
    for i in range(1, len(conclusions)):
        if conclusions[i] != conclusions[i - 1]:
            alternations += 1

    return alternations >= 2


def get_failing_jobs(owner, repo, run_id):
    """Get the list of failing jobs for a workflow run."""
    data = gh_api(f"repos/{owner}/{repo}/actions/runs/{run_id}/jobs?per_page=100")
    if not data or "jobs" not in data:
        return []

    failing = []
    for job in data["jobs"]:
        if job.get("conclusion") == "failure":
            failing.append({
                "name": job.get("name", ""),
                "url": job.get("html_url", ""),
            })
    return failing


def fetch_repo_ci(owner, repo, branch, days):
    """Fetch CI status for a single repo."""
    print(f"\nFetching CI for {owner}/{repo}...", file=sys.stderr)

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = gh_api(
        f"repos/{owner}/{repo}/actions/runs"
        f"?branch={branch}&per_page=100&created=%3E{since}"
    )

    if data is None or "workflow_runs" not in data:
        return {
            "owner": owner, "repo": repo, "branch": branch,
            "error": "Failed to fetch workflow runs",
            "workflows": [],
            "summary": {"total": 0, "passing": 0, "failing": 0, "flaky": 0},
        }

    runs = data["workflow_runs"]

    seen = {}
    for run in runs:
        wf_name = run.get("name", "unknown")
        if wf_name not in seen:
            seen[wf_name] = run

    now = datetime.now(timezone.utc)
    workflows = []

    for wf_name, run in seen.items():
        conclusion = run.get("conclusion", "")
        status = run.get("status", "")
        run_id = run.get("id", 0)
        workflow_id = run.get("workflow_id", 0)

        failing_jobs = []
        if conclusion == "failure":
            failing_jobs = get_failing_jobs(owner, repo, run_id)

        is_flaky = False
        if workflow_id and conclusion in ("success", "failure"):
            is_flaky = detect_flaky(owner, repo, workflow_id, branch)

        updated = run.get("updated_at", "")
        age_hours = 0
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                age_hours = int((now - updated_dt).total_seconds() / 3600)
            except (ValueError, TypeError):
                pass

        workflows.append({
            "name": wf_name,
            "run_id": run_id,
            "workflow_id": workflow_id,
            "status": status,
            "conclusion": conclusion or status,
            "url": run.get("html_url", ""),
            "updated_at": updated,
            "age_hours": age_hours,
            "head_sha": run.get("head_sha", "")[:7],
            "is_flaky": is_flaky,
            "failing_jobs": failing_jobs,
        })

    passing = sum(1 for w in workflows if w["conclusion"] == "success" and not w["is_flaky"])
    failing = sum(1 for w in workflows if w["conclusion"] == "failure" and not w["is_flaky"])
    flaky = sum(1 for w in workflows if w["is_flaky"])

    return {
        "owner": owner, "repo": repo, "branch": branch,
        "fetched_at": now.isoformat(),
        "error": None,
        "workflows": workflows,
        "summary": {
            "total": len(workflows),
            "passing": passing,
            "failing": failing,
            "flaky": flaky,
        },
    }


def load_repos(path):
    """Load repo list from config file."""
    with open(path) as f:
        return json.load(f).get("repos", [])


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub Actions CI status")
    parser.add_argument("owner", nargs="?", help="GitHub org")
    parser.add_argument("repo", nargs="?", help="Repo name")
    parser.add_argument("--repos-file", help="Path to repos.json for batch mode")
    parser.add_argument("--branch", default=None,
                        help="Branch to check (default: from repos.json or main)")
    parser.add_argument("--days", type=int, default=3,
                        help="Days of history to check (default: 3)")
    args = parser.parse_args()

    if args.repos_file:
        repos = load_repos(args.repos_file)
        results = []
        for r in repos:
            branch = args.branch or r.get("default_branch", "main")
            result = fetch_repo_ci(r["owner"], r["repo"], branch, args.days)
            results.append(result)

        output = {
            "mode": "batch",
            "total_repos": len(repos),
            "results": results,
            "aggregate": {
                "total_workflows": sum(r["summary"]["total"] for r in results),
                "passing": sum(r["summary"]["passing"] for r in results),
                "failing": sum(r["summary"]["failing"] for r in results),
                "flaky": sum(r["summary"]["flaky"] for r in results),
                "repos_with_errors": sum(1 for r in results if r["error"]),
                "repos_all_green": sum(
                    1 for r in results
                    if not r["error"] and r["summary"]["failing"] == 0 and r["summary"]["flaky"] == 0
                ),
            },
        }
    elif args.owner and args.repo:
        branch = args.branch or "main"
        output = fetch_repo_ci(args.owner, args.repo, branch, args.days)
    else:
        parser.error("Provide OWNER REPO or --repos-file")
        return

    json.dump(output, sys.stdout, indent=2)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()