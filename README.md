# OpportunityOS

Turn high-volume applications, registrations, and browser searches into repeatable opportunity workflows.

OpportunityOS packages agent skills for the messy operational layer behind finding and pursuing opportunities: searching portals, shortlisting matches, tracking candidates, preparing handoffs, filling low-risk fields, repairing required documents, and stopping before human-only actions such as CAPTCHA, legal acceptance, payment, identity verification, or final submission.

The repo is not just "admin automation." The higher-level purpose is to increase throughput and quality for opportunity creation: apartments, jobs, programs, marketplaces, registrations, and similar search-then-apply workflows.

## What It Helps With

- Search portals against explicit criteria and maintain a tracker.
- Prepare browser handoffs for applications, inquiries, registrations, or submissions.
- Repair low-quality ID scan PDFs when a workflow requires presentable documents.
- Separate agent-safe preparation from human-only decisions and submissions.
- Reuse the same workflow structure across apartments, jobs, vendors, programs, and other opportunity surfaces.

## Install With skills.sh

List the skills in this repo:

```bash
npx skills add https://github.com/ArthurZakirov/OpportunityOS --list
```

Install all skills for Codex:

```bash
npx skills add https://github.com/ArthurZakirov/OpportunityOS --skill '*' -a codex -g -y
```

Install one specific skill:

```bash
npx skills add https://github.com/ArthurZakirov/OpportunityOS --skill browser-search-and-handoff -a codex -g -y
```

## Install As A Claude Code Plugin

```text
/plugin marketplace add ArthurZakirov/OpportunityOS
/plugin install opportunityos@arthur-zakirov
```

Claude Code plugin skills are namespaced by plugin name, for example:

```text
/opportunityos:browser-search-and-handoff
```

## Install As A Codex Plugin

Add the marketplace:

```bash
codex plugin marketplace add ArthurZakirov/OpportunityOS
```

Then install from Codex with `/plugins`.

For local development from a cloned repo:

```bash
./scripts/setup-local-links.sh
```

Existing non-symlink paths are left untouched unless `--force` is used.

## Included Skills

<!-- BEGIN GENERATED SECTION: skills -->
> Generated from tracked `skills/*/SKILL.md` metadata.

| Skill | Description |
| --- | --- |
| `browser-search-and-handoff` | Human-in-the-loop workflow for browser-based sourcing, shortlisting, and next-step preparation across marketplaces and portals. Use when Codex needs to search websites for entities that match user-defined criteria, collect results in a tracker, find each entity's follow-up action page or application form, prefill low-risk fields where appropriate, and stop for human-only steps such as CAPTCHA, OTP, legal acceptance, payment, identity verification, or final submission. Typical triggers include apartment hunting, job search, dating or partner discovery, vendor sourcing, and similar search-then-contact or search-then-apply workflows. |
| `find-vc-backed-ai-jobs-munich` | Discover, evaluate, deduplicate, and store VC-backed AI startup jobs in Munich, Germany, and nearby/remote markets using web search, browser extraction, and a tracker or Notion database. |
| `gmail-opportunity-progress` | Monitor Gmail for job or opportunity application updates, classify messages such as confirmations, rejections, interview invites, assessments, and follow-ups, then update a tracker or Notion opportunity database without coupling to the application execution skill. |
| `job-application-operator` | Run schema-driven, remote-backed, human-configurable job application workflows with field inventory, safe autofill, document upload, learning, logging, and optional autonomous submission when policy allows. |
| `normalize-id-scan-pdf` | Repair low-quality or awkwardly laid-out ID scan PDFs. Use when a PDF of a personal ID, passport, or driver's license needs page content rotated without changing the page orientation, scaled up to use more of the page without clipping, renamed with stable bronze/silver/gold filenames, self-checked for cut-off content, or opened locally for final review. |
| `notion-opportunity-database` | Set up, maintain, and use a Notion opportunity database as the system of record for search, scoring, one-at-a-time application handoff, and status updates. |
| `opportunity-tool-selection` | Decide which tool mode to use for opportunity workflows: normal web search, browser automation, MCP/API access, local files, or chat-only reasoning. |
| `private-context-bootstrap` | Bootstrap private, remote-backed user context onto a fresh machine for opportunity workflows without committing personal data to public repositories. |
<!-- END GENERATED SECTION: skills -->

## Available Commands

<!-- BEGIN GENERATED SECTION: commands -->
> Generated from tracked `commands/*.md` files.

| Command | Summary |
| --- | --- |
| `/list-skills` | Please list all your available skills with a 1 sentence description for each one. Do not return any additional fluff text before or after. |
<!-- END GENERATED SECTION: commands -->

## Repo Inventory

<!-- BEGIN GENERATED SECTION: repo_inventory -->
> Generated from tracked manifests, scripts, commands, and skills.

```text
.
├── .agents/
│   ├── plugins/marketplace.json
│   └── skills -> ../skills
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .claude/
│   ├── commands -> ../commands
│   └── skills -> ../skills
├── .codex-plugin/
│   └── plugin.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
│       └── readme-generated.yml
├── commands/
│   └── list-skills.md
├── scripts/
│   ├── bootstrap-private-context.sh
│   ├── create-claude-command.sh
│   ├── create-shared-skill.sh
│   ├── generate-readme.py
│   ├── install-git-hooks.sh
│   ├── materialize-private-context.py
│   ├── setup-local-links.sh
│   ├── update-readme.sh
│   └── validate-private-context.py
├── skills/
│   ├── browser-search-and-handoff/
│   ├── find-vc-backed-ai-jobs-munich/
│   ├── gmail-opportunity-progress/
│   ├── job-application-operator/
│   ├── normalize-id-scan-pdf/
│   ├── notion-opportunity-database/
│   ├── opportunity-tool-selection/
│   └── private-context-bootstrap/
├── pyproject.toml
└── uv.lock
```
<!-- END GENERATED SECTION: repo_inventory -->

## Development

Use `./scripts/update-readme.sh` after adding or removing tracked skills, commands, scripts, or plugin metadata.
