# devtools-guardian

Automated monitoring and reporting for the Ansible Devtools Guardian role.

Fetches CI health, PR status, dependency updates, code coverage (Codecov), and SonarCloud quality gates across 18 Ansible Devtools repositories. Generates a live HTML dashboard deployed to GitHub Pages, markdown reports for Jira handoffs, and correlates CI failures to identify shared root causes.

## Quick Start

```bash
# Daily health check (PRs + CI + Dependencies + Coverage + Correlation)
python3 scripts/run_guardian_check.py --mode daily

# Weekly security audit (adds SonarCloud quality gates)
python3 scripts/run_guardian_check.py --mode weekly

# Sprint handoff report
python3 scripts/run_guardian_check.py --mode handoff
```

Reports are generated in `reports/` as markdown and JSON files.

## Prerequisites

- Python 3.10+
- [GitHub CLI](https://cli.github.com/) (`gh`) authenticated with `gh auth login`
- No external Python dependencies — uses only stdlib

## Individual Scripts

| Script | Purpose | Usage |
|---|---|---|
| `fetch_open_prs.py` | PR tracking with review status categorization | `python3 scripts/fetch_open_prs.py --repos-file config/repos.json` |
| `fetch_ci_status.py` | GitHub Actions workflow status + flaky detection | `python3 scripts/fetch_ci_status.py --repos-file config/repos.json` |
| `fetch_renovate_prs.py` | Dependency bot PRs with cooldown policy | `python3 scripts/fetch_renovate_prs.py --repos-file config/repos.json` |
| `fetch_codecov.py` | Code coverage from Codecov API | `python3 scripts/fetch_codecov.py --codecov-config config/codecov.json` |
| `fetch_sonar_gates.py` | SonarCloud quality gate status and metrics | `python3 scripts/fetch_sonar_gates.py --sonar-config config/sonar.json` |
| `correlate_failures.py` | CI failure correlation across repos | `python3 scripts/correlate_failures.py --ci FILE --renovate FILE` |
| `generate_report.py` | Markdown reports (prs, ci, renovate, codecov, sonar, guardian, handoff) | `python3 scripts/generate_report.py guardian --prs FILE --ci FILE` |
| `generate_dashboard.py` | Self-contained HTML dashboard | `python3 scripts/generate_dashboard.py --prs FILE --ci FILE -o docs/index.html` |

All fetch scripts output JSON to stdout. Pipe to a file or pass to the report generators.

## Dashboard (GitHub Pages)

The dashboard is automatically deployed via GitHub Actions:

- **Daily** (9:00 + 15:00 IST) — PRs, CI status, dependencies, code coverage, failure correlation
- **Weekly** (Monday 9:00 IST) — Full check including SonarCloud quality gates

View at: `https://sathyapramod.github.io/devtools-guardian/`

To trigger manually: Actions tab > select workflow > Run workflow.

### Dashboard Sections

| Section | Description |
|---|---|
| Health Overview | Summary cards for CI, PRs, Dependencies, Coverage, SonarCloud |
| Repository Status | Per-repo grid showing CI status, coverage %, and open PR count (matches the [official DevTools status page](https://docs.ansible.com/projects/team-devtools/stats/repos/)) |
| CI / Pipeline Health | Failing and flaky workflows with failing job details |
| Failure Correlation | Cross-repo failure clustering (temporal, shared job, dependency) |
| Open Pull Requests | PRs by category (ready, review, blocked, stale, draft) |
| Code Coverage | Codecov coverage per repo with lines/hits/misses |
| Dependency Updates | Overdue and pending dependency PRs |
| SonarCloud Quality | Quality gate status, bugs, vulnerabilities, code smells |

## CI Status Tracking

The guardian tracks two levels of CI health per repo:

- **All workflows** — Every GitHub Actions workflow on the default branch
- **Primary CI workflow** — The main CI workflow (`tox.yml`, `test.yml`, or `ci.yaml`) filtered by `event=schedule`, matching the [official status page](https://docs.ansible.com/projects/team-devtools/stats/repos/)

Use `--event schedule` to filter by scheduled runs only:

```bash
python3 scripts/fetch_ci_status.py --repos-file config/repos.json --event schedule
```

## PR Categories

| Category | Meaning |
|---|---|
| `ready_to_merge` | Approved, checks passing, no conflicts |
| `needs_review` | No reviews yet or review requested |
| `changes_requested` | Reviewer requested changes |
| `draft` | PR is in draft state |
| `stale` | No activity in 14+ days |
| `blocked` | Merge conflicts or failing checks |

## Dependency Cooldown Policy

| Update Type | Overdue After |
|---|---|
| Security | 3 days |
| Minor / Patch | 7 days |
| Major | 14 days |

## CI Failure Correlation

The correlation engine groups failures by likely root cause:

- **Temporal clusters** — Multiple repos failing within the same 2-hour window (infrastructure/runner issue)
- **Shared job failures** — Same job name failing across repos (shared tooling or config)
- **Dependency links** — Recent dependency update with failing checks + downstream test failures
- **Isolated failures** — Single-repo issues flagged separately

## Claude Code Skill

Install the `/guardian` skill for interactive use in Claude Code:

```bash
ln -s /path/to/devtools-guardian ~/.claude/plugins/devtools-guardian
```

Then in Claude Code:

```
/guardian              # run the skill
"what's failing?"      # natural language trigger
"show stale PRs"       # PR status
"correlate failures"   # failure analysis
"generate handoff"     # sprint handoff report
```

Remove with:

```bash
rm ~/.claude/plugins/devtools-guardian
```

## Configuration

- `config/repos.json` — Tracked repositories (owner, repo, default branch, CI workflow name)
- `config/sonar.json` — SonarCloud project key mappings
- `config/codecov.json` — Codecov-tracked repositories

Add a new repo by appending to `repos.json`. Add its SonarCloud project to `sonar.json` if applicable (key format: `{org}_{repo}`). Add to `codecov.json` if the repo publishes coverage to Codecov.

## Project Structure

```
devtools-guardian/
├── .claude-plugin/          # Claude Code plugin metadata
│   └── plugin.json
├── .github/workflows/       # GitHub Actions (daily + weekly cron)
│   ├── guardian-daily.yml
│   └── guardian-weekly.yml
├── config/
│   ├── repos.json           # 17 tracked repositories with CI workflow config
│   ├── sonar.json           # SonarCloud project mappings
│   └── codecov.json         # Codecov-tracked repositories
├── scripts/
│   ├── fetch_open_prs.py
│   ├── fetch_ci_status.py
│   ├── fetch_renovate_prs.py
│   ├── fetch_codecov.py
│   ├── fetch_sonar_gates.py
│   ├── correlate_failures.py
│   ├── generate_report.py
│   ├── generate_dashboard.py
│   └── run_guardian_check.py
├── skills/guardian/          # Claude Code skill
│   ├── SKILL.md
│   └── references/
│       └── commands.md
└── reports/                  # Generated output (gitignored)
```
