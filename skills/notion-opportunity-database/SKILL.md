---
name: notion-opportunity-database
description: Set up, maintain, and use a Notion opportunity database as the system of record for search, scoring, one-at-a-time application handoff, and status updates.
---

# Notion Opportunity Database

## Purpose

Use this skill when a Notion database should act as the system of record for opportunity workflows.

The database owns discovery, deduplication, scoring, rationale, application handoff, and post-action status. It should feed one selected opportunity at a time into execution skills such as `job-application-operator`.

## Tool Boundary

Use Notion MCP/API tools for:

- fetching database schema
- querying candidate rows
- checking duplicates
- creating rows
- updating row properties
- changing schema and views
- writing application status back

Do not use browser automation to edit Notion if MCP/API access is available.

## Recommended Schema

Minimum fields:

- `Role` or `Name`: title
- `URL`: URL
- `Company`: text
- `Status`: select
- `Priority Score`: number, 0-100
- `Rationale`: rich text
- `Role Family`: select
- `Location`: multi-select
- `Salary Range`: text
- `Salary Rationale`: rich text
- `Source`: select

`URL` should be one of the first visible columns, ideally immediately after the title.

## Status Semantics

`Status` is the application/execution state. It is not a priority or fit label.

Recommended values:

- `Needs enrichment`: found or imported, but fit, score, rationale, salary, or source fields are incomplete
- `Enriching`: an agent is researching and completing the row
- `Backlog`: enriched and scored, not yet selected for application work
- `To do`: selected from the backlog for the next application work batch
- `In progress`: application form is being inspected, filled, or prepared
- `Human blocked`: requires user action, login, CAPTCHA, missing information, unknown required field, or a policy decision
- `Ready to apply`: application is prepared and waiting for final submission/review
- `Submitted`: application has been submitted
- `Waiting for response`: submitted and waiting for company response
- `Interview invite`: company invited the candidate to book an interview, but it is not scheduled yet
- `Interview scheduled`: interview is booked on the calendar or otherwise confirmed
- `Interview completed`: interview happened and the candidate is waiting for the next response
- `Assessment received`: company sent an online assessment/challenge, but work has not started
- `Assessment in progress`: assessment/challenge is actively being worked
- `Assessment submitted`: assessment/challenge was submitted and the candidate is waiting for the next response
- `Rejected`: rejected or self-rejected after application
- `Closed`: job is no longer open

Use `Priority Score` for ranking and `Rationale` for fit explanation.

Expected flow:

```text
Needs enrichment -> Enriching -> Backlog -> To do -> In progress -> Ready to apply -> Submitted -> Waiting for response
```

`Human blocked` is a branch from `In progress`; return to `In progress` or `Ready to apply` after the blocker is resolved.

Company responses branch after submission:

```text
Waiting for response -> Interview invite -> Interview scheduled -> Interview completed -> Waiting for response
Waiting for response -> Assessment received -> Assessment in progress -> Assessment submitted -> Waiting for response
Waiting for response -> Rejected
```

## Enrichment Criteria

A row is enriched enough for `Backlog` when it has:

- valid `URL`
- `Company`
- `Role Family`
- `Location`
- numeric `Priority Score`
- consolidated `Rationale`
- `Source`
- `Salary Range` when a credible value is available, otherwise empty
- `Salary Rationale` explaining source, confidence, or why salary is unknown

Use `Needs enrichment` for raw imports and partially captured roles. Use `Enriching` while an agent is actively researching the row. Do not move a row to `To do` until it is in `Backlog` unless the user explicitly chooses to apply without full enrichment.

## Rationale Field

Keep one consolidated `Rationale` field instead of separate columns for:

- fit rationale
- experience signal
- application angle
- main risk

Recommended structure:

```text
Fit: ...
Experience signal: ...
Application angle: ...
Main risk: ...
```

## Salary Fields

Keep the value separate from the reasoning:

- `Salary Range`: only the actual range or value, such as `EUR 80k-100k base` or empty if unknown
- `Salary Rationale`: source, confidence, or why the value is unknown

Do not put sentences like `not captured; verify directly` in `Salary Range`.

## One-At-A-Time Application Handoff

Before invoking an execution skill:

1. Fetch the database schema.
2. Select one row by status and score, normally highest `Priority Score` where `Status` is `To do`.
3. Confirm the row has a valid `URL`.
4. Update `Status` to `In progress`.
5. Pass a compact handoff object to `job-application-operator`.

Handoff object:

```yaml
source: notion
pageId:
role:
company:
applicationUrl:
priorityScore:
rationale:
salaryRange:
salaryRationale:
roleFamily:
location:
statusBefore:
```

The application operator should work on exactly that one job, then return a structured outcome.

## Writeback After Application

After execution, update the Notion row:

- `Status`: `Ready to apply`, `Submitted`, `Human blocked`, `Closed`, or another application-stage value
- `Rationale`: append concise application outcome notes if they materially change the decision
- `Salary Range` and `Salary Rationale`: update only if the application revealed reliable compensation information

Do not overwrite source rationale with application logs. Keep detailed field inventories and sensitive application details in private logs.

## Discovery Insert Rules

Before creating a row, deduplicate by:

- exact URL
- normalized URL domain/path
- company + role title

If a duplicate exists, update missing fields and leave application status intact unless the job is closed or reopened.

## Output

Return:

- database used
- selected row
- handoff object
- status before and after
- fields updated
- blockers
