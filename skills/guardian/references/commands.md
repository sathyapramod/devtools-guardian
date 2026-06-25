# Guardian Command Reference

## Script Locations

All scripts are in the `scripts/` directory at the repo root.
Config files are in `config/`. Reports are generated in `reports/`.

## fetch_open_prs.py

```bash
# Single repo
python3 scripts/fetch_open_prs.py ansible ansible-lint

# All repos
python3 scripts/fetch_open_prs.py --repos-file config/repos.json

# Custom stale threshold
python3 scripts/fetch_open_prs.py --repos-file config/repos.json --stale-days 14

# Include bot PR details
python3 scripts/fetch_open_prs.py --repos-file config/repos.json --include-bots
```

**PR Categories:**
- `ready_to_merge` — approved, checks passing, no conflicts
- `needs_review` — no reviews yet or review requested
- `changes_requested` — reviewer requested changes
- `draft` — PR is in draft state
- `stale` — no activity in 14+ days
- `blocked` — merge conflicts or failing checks

## fetch_ci_status.py

```bash
# Single repo
python3 scripts/fetch_ci_status.py ansible ansible-lint

# All repos, last 3 days
python3 scripts/fetch_ci_status.py --repos-file config/repos.json

# Custom time range
python3 scripts/fetch_ci_status.py --repos-file config/repos.json --days 7

# Scheduled runs only (matches official DevTools status page)
python3 scripts/fetch_ci_status.py --repos-file config/repos.json --event schedule
```

**Primary CI tracking:** Each repo's main CI workflow (configured via
`ci_workflow` in repos.json) is tracked separately using `event=schedule`,
matching the official Ansible DevTools status page badges.

**Flaky detection:** A workflow is flagged as flaky if its last 5 runs
alternate between success and failure 2+ times.

## fetch_renovate_prs.py

```bash
# Single repo
python3 scripts/fetch_renovate_prs.py ansible ansible-lint

# All repos
python3 scripts/fetch_renovate_prs.py --repos-file config/repos.json
```

**Cooldown thresholds:**
- Security updates: overdue after 3 days
- Minor/patch updates: overdue after 7 days
- Major version bumps: overdue after 14 days

## fetch_sonar_gates.py

```bash
# All projects
python3 scripts/fetch_sonar_gates.py --sonar-config config/sonar.json

# Single project
python3 scripts/fetch_sonar_gates.py --project-key ansible_ansible-lint

# With authentication
SONAR_TOKEN=xxx python3 scripts/fetch_sonar_gates.py --sonar-config config/sonar.json
```

**Metrics fetched:** coverage, bugs, vulnerabilities, code_smells,
duplicated_lines_density, security_hotspots, ncloc, reliability_rating,
security_rating, sqale_rating.

## fetch_codecov.py

```bash
# All repos from codecov config
python3 scripts/fetch_codecov.py --codecov-config config/codecov.json

# All repos from repos.json
python3 scripts/fetch_codecov.py --repos-file config/repos.json

# Single repo
python3 scripts/fetch_codecov.py ansible ansible-lint
```

**Metrics fetched:** coverage percentage, lines, hits, misses, branches,
language, and active status per repo. Aggregates include average/min/max
coverage, repos above 80%, and repos below 50%.

## correlate_failures.py

```bash
# CI data only
python3 scripts/correlate_failures.py --ci reports/ci-status.json

# With dependency correlation
python3 scripts/correlate_failures.py --ci reports/ci-status.json --renovate reports/renovate-prs.json

# Save to file
python3 scripts/correlate_failures.py --ci reports/ci-status.json -o reports/correlation.json
```

**Cluster types:**
- `temporal` — repos failing within 2-hour window
- `shared_job` — same job name failing across 2+ repos
- `dependency` — failing dependency PR + downstream test failures

## generate_report.py

```bash
# Individual reports
python3 scripts/generate_report.py prs reports/open-prs.json
python3 scripts/generate_report.py ci reports/ci-status.json
python3 scripts/generate_report.py renovate reports/renovate-prs.json
python3 scripts/generate_report.py codecov reports/codecov.json
python3 scripts/generate_report.py sonar reports/sonar-gates.json

# Consolidated reports
python3 scripts/generate_report.py guardian --prs FILE --ci FILE --renovate FILE --codecov FILE --sonar FILE
python3 scripts/generate_report.py handoff --prs FILE --ci FILE --renovate FILE --codecov FILE --sonar FILE

# Write to file
python3 scripts/generate_report.py prs reports/open-prs.json -o reports/pr-dashboard.md
```

## run_guardian_check.py

```bash
# Daily (PRs + CI + Dependencies + Coverage)
python3 scripts/run_guardian_check.py --mode daily

# Weekly (Daily + SonarCloud)
python3 scripts/run_guardian_check.py --mode weekly

# Handoff (Weekly + Jira template)
python3 scripts/run_guardian_check.py --mode handoff
```

**Exit codes:** 0 = all green, 1 = issues found, 2 = script errors.
