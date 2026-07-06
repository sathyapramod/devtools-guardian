# Security Audit Report — 2026-07-07

**Auditor:** Guardian (automated)
**Scope:** 15 repos across `ansible` org (main branch only)
**Open PRs scanned:** 60 (30 human + 30 bot)
**Period focus:** 2026-06-30 to 2026-07-06

---

## Executive Summary

| Category | Count | Risk |
|---|---|---|
| Overdue dependency PRs (>7d) | 11 | **HIGH** — 3 repos at 21-49 days |
| Unresolved critical findings (prior review) | 0 | CLEAR — vscode-ansible#2721 closed |
| Security-relevant merges this week | 7 | CLEAR — CVE patches + GHA hardening |
| Flaky CI workflows | 4 | MEDIUM — intermittent failures |
| CI startup failures | 2 | MEDIUM — ansible-creator tox/push broken |
| Failing CI workflows | 0 | CLEAR |
| Open security-tagged dependency PRs | 0 | CLEAR |
| PRs ready to merge | 1 | LOW — vscode-ansible#3003 |

**Overall posture: ATTENTION NEEDED** — 11 overdue Renovate dependency PRs (oldest 49 days in ansible-navigator), and ansible-creator CI has startup failures. The vscode-ansible#2721 shell injection PR was **closed without merge**, resolving last week's P1.

---

## Operational Action Items

| Priority | Action | Repo | Target |
|---|---|---|---|
| **P1** | Merge overdue Renovate PR [#2120](https://github.com/ansible/ansible-navigator/pull/2120) — **49 days** pending, CI passing | ansible-navigator | Immediate |
| **P1** | Merge overdue Renovate PR [#106](https://github.com/ansible/ansible-content-actions/pull/106) — **42 days** pending, CI passing | ansible-content-actions | Immediate |
| **P1** | Investigate and fix `startup_failure` on `tox` and `push` workflows | ansible-creator | This week |
| **P2** | Merge overdue Renovate PRs [#4647](https://github.com/ansible/molecule/pull/4647)/[#4646](https://github.com/ansible/molecule/pull/4646) — **21 days** pending | molecule | This week |
| **P2** | Merge overdue Renovate PR [#597](https://github.com/ansible/ansible-compat/pull/597) — **21 days** pending | ansible-compat | This week |
| **P2** | Merge overdue Renovate PRs [#5082](https://github.com/ansible/ansible-lint/pull/5082)/[#5081](https://github.com/ansible/ansible-lint/pull/5081) — **14 days**, CI passing | ansible-lint | This week |
| **P2** | Verify ansible-sign Renovate PRs [#119](https://github.com/ansible/ansible-sign/pull/119)/[#120](https://github.com/ansible/ansible-sign/pull/120) cover the 23 CVEs from prior fix branch | ansible-sign | This week |
| **P3** | Review and merge fresh Renovate dependency batch (19 new PRs) per cooldown policy | Fleet-wide | Per policy |
| **P3** | Resolve `action_required` on tox workflow | ansible-dev-tools | This week |

---

## Vulnerabilities & Findings

### RESOLVED — vscode-ansible#2721 Shell Injection

**PR:** [ansible/vscode-ansible#2721](https://github.com/ansible/vscode-ansible/pull/2721) — persistent EE container
**Previous status:** 3 Critical + 3 Major security findings, stale 73+ days
**Current status:** **CLOSED** (not merged) on 2026-07-01

The PR with shell injection, volume mount, and lockfile vulnerabilities was closed without merge. No further action required.

### OPEN — ansible-sign CVE Remediation Pending

**PRs:** [#119](https://github.com/ansible/ansible-sign/pull/119) (deps) + [#120](https://github.com/ansible/ansible-sign/pull/120) (pep621)
**Status:** Open, CI pending (opened Jul 6)

Last week's audit flagged 23 CVEs across 6 packages in ansible-sign. These new Renovate PRs may cover the fixes. Verification needed before merge.

---

## CI Health

### All Repos — Main Branch Status

| Repository | Workflows | Passing | Failing | Flaky | Status |
|---|---|---|---|---|---|
| actions | 6 | 6 | 0 | 0 | GREEN |
| ansible-compat | 4 | 3 | 0 | 1 | FLAKY — `finalize` |
| ansible-content-actions | 1 | 1 | 0 | 0 | GREEN |
| ansible-creator | 4 | 1 | 0 | 0 | DEGRADED — `tox` + `push` startup_failure |
| ansible-dev-environment | 2 | 2 | 0 | 0 | GREEN |
| ansible-dev-tools | 4 | 2 | 0 | 0 | ATTENTION — `tox` action_required |
| ansible-lint | 3 | 2 | 0 | 1 | FLAKY — `finalize` |
| ansible-navigator | 1 | 0 | 0 | 1 | FLAKY — `tox` |
| ansible-sign | 2 | 2 | 0 | 0 | GREEN |
| mkdocs-ansible | 2 | 1 | 0 | 0 | GREEN |
| molecule | 5 | 5 | 0 | 0 | GREEN |
| pytest-ansible | 4 | 4 | 0 | 0 | GREEN |
| team-devtools | 3 | 2 | 0 | 1 | FLAKY — `Graph Update` |
| tox-ansible | 5 | 5 | 0 | 0 | GREEN |
| vscode-ansible | 3 | 2 | 0 | 0 | GREEN |

**Aggregate:** 49 workflows total | 38 passing | 0 failing | 4 flaky | 11 repos all-green

---

## Overdue Dependency PRs (>7 day cooldown exceeded)

| Repo | PR | Title | Age | Checks | Action |
|---|---|---|---|---|---|
| ansible-navigator | [#2120](https://github.com/ansible/ansible-navigator/pull/2120) | update all dependencies | **49d** | passing | Merge now — exceeds 30d stale threshold |
| ansible-content-actions | [#106](https://github.com/ansible/ansible-content-actions/pull/106) | update all dependencies | **42d** | passing | Merge now — exceeds 30d stale threshold |
| molecule | [#4647](https://github.com/ansible/molecule/pull/4647) | update pep621 | **21d** | pending | Review and merge |
| molecule | [#4646](https://github.com/ansible/molecule/pull/4646) | update all dependencies | **21d** | passing | Merge — CI green |
| ansible-compat | [#597](https://github.com/ansible/ansible-compat/pull/597) | update pep621 | **21d** | pending | Review and merge |
| ansible-lint | [#5082](https://github.com/ansible/ansible-lint/pull/5082) | update all dependencies pep621 | **14d** | passing | Merge — CI green |
| ansible-lint | [#5081](https://github.com/ansible/ansible-lint/pull/5081) | update all dependencies | **14d** | passing | Merge — CI green |
| mkdocs-ansible | [#315](https://github.com/ansible/mkdocs-ansible/pull/315) | bump python deps pep621 | **14d** | pending | Review when CI resolves |
| mkdocs-ansible | [#314](https://github.com/ansible/mkdocs-ansible/pull/314) | bump python deps | **14d** | failing | Fix CI failure before merge |
| pytest-ansible | [#592](https://github.com/ansible/pytest-ansible/pull/592) | update pep621 | **14d** | pending | Review and merge |
| vscode-ansible | [#2924](https://github.com/ansible/vscode-ansible/pull/2924) | update js-yaml to v5 | **13d** | passing | Merge — CI green |

---

## New Dependency PRs This Week (Renovate — opened Jul 6)

Bulk dependency update cycle. All are routine minor updates with 7-day cooldown.

| Repo | PRs | CI Status |
|---|---|---|
| actions | [#140](https://github.com/ansible/actions/pull/140), [#139](https://github.com/ansible/actions/pull/139) | pending / failing |
| ansible-creator | [#619](https://github.com/ansible/ansible-creator/pull/619), [#618](https://github.com/ansible/ansible-creator/pull/618) | pending / failing |
| ansible-dev-environment | [#443](https://github.com/ansible/ansible-dev-environment/pull/443), [#442](https://github.com/ansible/ansible-dev-environment/pull/442) | pending / passing |
| ansible-dev-tools | [#781](https://github.com/ansible/ansible-dev-tools/pull/781), [#780](https://github.com/ansible/ansible-dev-tools/pull/780) | pending / failing |
| ansible-sign | [#120](https://github.com/ansible/ansible-sign/pull/120), [#119](https://github.com/ansible/ansible-sign/pull/119) | pending / passing |
| pytest-ansible | [#596](https://github.com/ansible/pytest-ansible/pull/596) | failing |
| team-devtools | [#500](https://github.com/ansible/team-devtools/pull/500), [#499](https://github.com/ansible/team-devtools/pull/499) | pending / passing |
| tox-ansible | [#579](https://github.com/ansible/tox-ansible/pull/579), [#578](https://github.com/ansible/tox-ansible/pull/578) | pending / failing |
| vscode-ansible | [#2999](https://github.com/ansible/vscode-ansible/pull/2999) | passing |
| mkdocs-ansible | [#316](https://github.com/ansible/mkdocs-ansible/pull/316) | passing |
| ansible-compat | [#603](https://github.com/ansible/ansible-compat/pull/603) | failing |

**Action:** Let new Renovate PRs pass CI. Merge per cooldown policy (7d minor). Spot-check ansible-sign PRs for CVE coverage.

---

## Open Human PRs — Security Relevance Check

30 human PRs open across 7 repos. 1 ready to merge.

| Repo | PR | Title | Author | Age | Status | Security? |
|---|---|---|---|---|---|---|
| vscode-ansible | [#3003](https://github.com/ansible/vscode-ansible/pull/3003) | refactor: reduce cognitive complexity in lightspeed view handlers | omaciel | 0d | **Ready to merge** | No |
| ansible-lint | [#5102](https://github.com/ansible/ansible-lint/pull/5102) | fix: jinja[spacing] minus modifiers | Dotify71 | 0d | Needs review | No |
| ansible-dev-tools | [#782](https://github.com/ansible/ansible-dev-tools/pull/782) | chore: Delete Skill.md | AndromedaCLI | 0d | Needs review | No |
| ansible-navigator | [#2134](https://github.com/ansible/ansible-navigator/pull/2134) | limited support for Apple container | jwalzer | 3d | Needs review | Low — container config |
| ansible-lint | [#5097](https://github.com/ansible/ansible-lint/pull/5097) | fix: add plain-name role mocks for --offline | muhamedfazalps | 3d | Changes requested | No |
| ansible-lint | [#5095](https://github.com/ansible/ansible-lint/pull/5095) | fix: handle register projections in var-naming | muhamedfazalps | 4d | Needs review | No |
| ansible-lint | [#5091](https://github.com/ansible/ansible-lint/pull/5091) | fix: propagate extra_vars to import_playbook | apoorva-01 | 5d | Needs review | No |
| vscode-ansible | [#2977](https://github.com/ansible/vscode-ansible/pull/2977) | chore: SonarCloud coverage config | ssbarnea | 5d | Draft | No |
| ansible-lint | [#5088](https://github.com/ansible/ansible-lint/pull/5088) | fix: apply profile-level skip_list | muhamedfazalps | 7d | Needs review | No |
| molecule | [#4651](https://github.com/ansible/molecule/pull/4651) | fix: share ephemeral directory | p3trk | 10d | Needs review | No |
| ansible-lint | [#5068](https://github.com/ansible/ansible-lint/pull/5068) | fix: respect skip_list for yaml[comments] | kaizeenn | 22d | Needs review | No |
| vscode-ansible | [#2899](https://github.com/ansible/vscode-ansible/pull/2899) | fix: suppress repeated PET warning | gygitlab | 18d | Changes requested | No |
| vscode-ansible | [#2891](https://github.com/ansible/vscode-ansible/pull/2891) | feat: add pullNewer option to Devcontainer | sathyapramod | 19d | Changes requested | No |
| vscode-ansible | [#2881](https://github.com/ansible/vscode-ansible/pull/2881) | feat: add ansible.config.path | ivan-mezentsev | 20d | Changes requested | No |
| ansible-lint | [#5055](https://github.com/ansible/ansible-lint/pull/5055) | fix: resolve nested include_tasks paths | cyphercodes | 38d | Changes requested | No |
| ansible-content-actions | [#107](https://github.com/ansible/ansible-content-actions/pull/107) | fix: pin actions to commit sha | jon4hz | 35d | Needs review | Low — supply chain |
| ansible-content-actions | [#103](https://github.com/ansible/ansible-content-actions/pull/103) | feat: add Galaxy server auth inputs | djdanielsson | 81d | Needs review | Low — auth inputs |
| ansible-lint | [#5016](https://github.com/ansible/ansible-lint/pull/5016) | feat: add event-query rule | stevefulme1 | 86d | Needs review | No |
| ansible-compat | [#575](https://github.com/ansible/ansible-compat/pull/575) | Add .yaml as valid extension | olipinski | 88d | Needs review | No |
| ansible-navigator | [#2112](https://github.com/ansible/ansible-navigator/pull/2112) | feat: fail-fast with non-existent playbooks | brookelew | 90d | Draft | No |
| molecule | [#4623](https://github.com/ansible/molecule/pull/4623) | fix: display schema validation errors | chronicc | 106d | Draft | No |
| molecule | [#4617](https://github.com/ansible/molecule/pull/4617) | feat: add --slice flag | cidrblock | 128d | Draft | No |

**No security-critical human PRs this week.** Two low-risk items worth noting:
- ansible-content-actions#107 pins GHA actions to commit SHAs (supply chain hardening — positive)
- ansible-content-actions#103 adds Galaxy auth inputs (review auth handling before merge)

---

## Flagged Commits — Security-Relevant Merges (Jun 30 — Jul 6)

| Date | Repo | PR | Description | CVE / Advisory |
|---|---|---|---|---|
| Jul 06 | actions | [#138](https://github.com/ansible/actions/pull/138) | resolve code-scanning and dependabot security vulnerabilities | Multiple |
| Jul 04 | ansible-dev-tools | [#779](https://github.com/ansible/ansible-dev-tools/pull/779) | bump pydantic-settings to 2.14.2 — symlink traversal fix | Symlink traversal |
| Jul 04 | team-devtools | [#498](https://github.com/ansible/team-devtools/pull/498) | upgrade cryptography to 49.0.0 | Multiple CVEs |
| Jul 04 | molecule | [#4653](https://github.com/ansible/molecule/pull/4653) | add explicit permissions to release workflow jobs | GHA hardening |
| Jul 04 | ansible-creator | [#617](https://github.com/ansible/ansible-creator/pull/617) | add explicit permissions to GHA workflows | GHA hardening |
| Jul 03 | vscode-ansible | [#3000](https://github.com/ansible/vscode-ansible/pull/3000) | resolve 7 dependabot security vulnerabilities | 7 Dependabot alerts |
| Jul 03 | ansible-dev-tools | [#775](https://github.com/ansible/ansible-dev-tools/pull/775) | update base image to Fedora 44 (F42 EOL) | EOL platform |

**Summary:** 7 security-relevant commits merged. Key themes: Dependabot/code-scanning vuln resolution, cryptography CVE patch, pydantic symlink traversal fix, GHA permissions hardening, and EOL base image update.

---

## Repository Status

| Repository | Open PRs | Bot PRs | CI Status | Last Activity | Security |
|---|---|---|---|---|---|
| actions | 3 (3 draft) | 2 | GREEN | Jul 06 | Code-scanning vulns fixed |
| ansible-compat | 2 (1 draft) | 2 | FLAKY | Jul 06 | Clean |
| ansible-content-actions | 2 | 1 | GREEN | Jul 06 | Clean |
| ansible-creator | 0 | 2 | DEGRADED | Jul 04 | GHA perms hardened |
| ansible-dev-environment | 0 | 2 | GREEN | Jul 06 | Clean |
| ansible-dev-tools | 1 | 2 | ATTENTION | Jul 06 | pydantic symlink fix |
| ansible-lint | 9 | 2 | FLAKY | Jul 06 | Clean |
| ansible-navigator | 2 (1 draft) | 1 | FLAKY | Jul 06 | Clean |
| ansible-sign | 0 | 2 | GREEN | Jul 06 | 23 CVEs pending (Renovate) |
| mkdocs-ansible | 0 | 3 | GREEN | Jul 06 | Clean |
| molecule | 5 (3 draft) | 2 | GREEN | Jul 06 | GHA perms hardened |
| pytest-ansible | 0 | 2 | GREEN | Jul 06 | Clean |
| team-devtools | 0 | 2 | FLAKY | Jul 06 | cryptography CVE fixed |
| tox-ansible | 0 | 2 | GREEN | Jul 06 | Clean |
| vscode-ansible | 6 (2 draft) | 3 | GREEN | Jul 06 | 7 dependabot vulns fixed |

---

## Carry-Forward

| Item | Status | Notes |
|---|---|---|
| vscode-ansible#2721 shell injection | **RESOLVED** | PR closed without merge on Jul 1 |
| ansible-sign 23 CVEs | Pending | Renovate PRs #119/#120 opened Jul 6 — verify coverage |
| ansible-navigator overdue deps | Still open | Now 49 days — exceeds 30d stale threshold |
| ansible-content-actions overdue deps | Still open | Now 42 days — exceeds 30d stale threshold |

---

*Generated with AI assistance: Claude Code / Opus 4.6 (Anthropic)*
