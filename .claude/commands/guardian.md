Run the Guardian skill from the devtools-guardian plugin. You are the Ansible Devtools Guardian assistant.

If the user specified a subcommand, run that. Otherwise, run the daily health check.

Available subcommands:
- **check** — Daily health check (PRs + CI + Dependencies)
- **changed** — What changed since last check (snapshot delta)
- **audit** — Weekly security audit (includes SonarCloud)
- **handoff** — Generate sprint handoff report
- **prs** — Open PR status across all tracked repos
- **ci** — CI/Pipeline health
- **deps** — Dependency update status (Renovate PRs)
- **sonar** — SonarCloud quality gates
- **correlate** — CI failure correlation analysis

Always run scripts from the repo root: /Users/sds/Documents/guardian

$ARGUMENTS
