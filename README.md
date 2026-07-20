# devtools-guardian (moved)

> **This repository is deprecated.**
>
> Guardian skill, scripts, config, and scheduled workflows now live in
> [`ansible/team-devtools`](https://github.com/ansible/team-devtools)
> under [`.agents/skills/td-guardian`](https://github.com/ansible/team-devtools/tree/main/.agents/skills/td-guardian).
>
> Cron + GitHub Pages dashboards are (or will be) run from
> `ansible/team-devtools` via `.github/workflows/guardian-*.yml`.
> Snapshot baselines continue to use Pages `snapshot.json` (not pushes to
> protected `main`).

## What to use instead

| Need | Where |
|------|--------|
| Skill + scripts | `ansible/team-devtools/.agents/skills/td-guardian/` |
| Install locally | `/td-skill-refresh` or clone skills via team-devtools bootstrap |
| Daily / weekly dashboard | Actions on `ansible/team-devtools` (`guardian-daily.yml` / `guardian-weekly.yml`) |
| Agent invocation | `/td-guardian` |

Please open issues and PRs against **ansible/team-devtools**, not this repo.

The Actions workflows in this repository should be **disabled** once Pages and
secrets (`SONAR_TOKEN`, `AUDIT_GH_TOKEN`, `GUARDIAN_GH_TOKEN`) are configured on
team-devtools and a successful daily deploy has been verified.
