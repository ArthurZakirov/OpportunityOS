# Notion Job Application Pipeline TODO

This is the remaining work for the Notion-backed job application pipeline after the Notion connector started timing out.

## Current Known State

- Database: `AI / FDE Job Research - Munich & Germany`
- Database URL: `https://www.notion.so/228431e384844d17a5142863f1e1ffda`
- Data source: `collection://827f552a-8b41-4b1a-b984-33caa857f02d`
- `Application Pipeline` view was successfully changed from grouping by `Role Family` to grouping by `Status`.
- Some status/page updates timed out, so do not assume all rows are backfilled.
- OpportunityOS repo-side skills have been updated, including the new `gmail-opportunity-progress` skill.

## Desired Status Options

Use these `Status` select options in this order:

1. `Needs enrichment`
2. `Enriching`
3. `Backlog`
4. `To do`
5. `In progress`
6. `Human blocked`
7. `Ready to apply`
8. `Submitted`
9. `Waiting for response`
10. `Interview invite`
11. `Interview scheduled`
12. `Interview completed`
13. `Assessment received`
14. `Assessment in progress`
15. `Assessment submitted`
16. `Rejected`
17. `Closed`

## Status Semantics

- `Needs enrichment`: discovered or imported, but fit, score, rationale, salary, or source fields are incomplete.
- `Enriching`: an agent is actively researching and completing the row.
- `Backlog`: enriched and scored, but not selected for application work.
- `To do`: selected from backlog for the next application batch.
- `In progress`: agent or human is inspecting, filling, or preparing the application.
- `Human blocked`: user action is needed, such as login, CAPTCHA, missing information, policy decision, or unclear required field.
- `Ready to apply`: application is prepared and waiting for final review/submission.
- `Submitted`: application has been submitted.
- `Waiting for response`: waiting for company response after submission or after a completed step.
- `Interview invite`: company invited the candidate to book an interview, but it is not booked yet.
- `Interview scheduled`: interview is booked or otherwise confirmed.
- `Interview completed`: interview happened and next communication is pending.
- `Assessment received`: company sent an online assessment/challenge, but work has not started.
- `Assessment in progress`: assessment/challenge is actively being worked.
- `Assessment submitted`: assessment/challenge was submitted and next communication is pending.
- `Rejected`: company rejected the candidate or the opportunity was self-rejected after review.
- `Closed`: posting is closed or no longer actionable.

## Normal Pipeline

```text
Needs enrichment -> Enriching -> Backlog -> To do -> In progress -> Ready to apply -> Submitted -> Waiting for response
```

`Human blocked` branches from `In progress` and then returns to `In progress` or `Ready to apply` after the blocker is resolved.

Company response branches:

```text
Waiting for response -> Interview invite -> Interview scheduled -> Interview completed -> Waiting for response
Waiting for response -> Assessment received -> Assessment in progress -> Assessment submitted -> Waiting for response
Waiting for response -> Rejected
```

## Remaining Notion Work

1. Re-fetch the database through the Notion plugin and verify the current schema.
2. Confirm whether the expanded `Status` options above already partially applied.
3. If missing, update the `Status` select options to the full desired list above.
4. Re-fetch the `Application Pipeline` view and verify:
   - view type is `board`
   - grouped by `Status`
   - sorted by `Priority Score` descending
   - visible card properties include `Role`, `URL`, `Company`, `Priority Score`, `Rationale`, `Salary Range`, `Salary Rationale`, and `Source`
5. Query all rows in the data source.
6. Set blank `Status` based on enrichment completeness:
   - `Backlog` if the row has URL, company, role family, location, priority score, rationale, source, and salary rationale.
   - `Needs enrichment` if those fields are incomplete.
7. Set known closed postings to `Closed`.
8. Do not set rows to `To do` automatically unless explicitly selecting a work batch.
9. Verify there are no rows with blank `Status`.
10. Verify every job page has the `💼` page icon.
11. Verify `Salary Range` contains only clean values/ranges, not prose.
12. Verify salary reasoning/provenance lives in `Salary Rationale`.
13. Verify `URL` is one of the first visible columns in table views.
14. Verify removed columns are still gone:
    - `Priority`
    - `Application Angle`
    - `Experience Signal`
    - `Fit Rationale`
    - `Main Risk`
    - `Company Website`
    - `Date`

## Known Row Backfill Policy

Default:

- Set raw or incomplete rows to `Needs enrichment`.
- Set rows actively being researched to `Enriching`.
- Set enriched, ranked rows to `Backlog`.
- Set only clearly queued rows to `To do`.
- Set closed/unavailable postings to `Closed`.

Do not infer application progress without evidence from the application operator, tracker notes, or Gmail.

## Enrichment Completeness

A row is enriched enough for `Backlog` when it has:

- valid `URL`
- `Company`
- `Role Family`
- `Location`
- numeric `Priority Score`
- consolidated `Rationale`
- `Source`
- `Salary Range` if credible, otherwise blank
- `Salary Rationale` explaining source, confidence, or why salary is unknown

Rows missing those fields should stay in `Needs enrichment` until an agent researches them.

## Gmail Progress Skill Follow-Up

The new `OpportunityOS/skills/gmail-opportunity-progress/SKILL.md` should be used later to:

1. Search Gmail for job/application messages.
2. Classify each relevant email as confirmation, rejection, interview invite, scheduled interview, assessment, reminder, submitted assessment, or company question.
3. Match each message to exactly one Notion row.
4. Update `Status` only when the match and event type are clear.
5. Report ambiguous emails instead of guessing.

## Notion Connector Recovery Checklist

When the Notion plugin starts responding again:

1. Start with a fetch-only call.
2. Avoid large parallel write batches until one small update succeeds.
3. Re-fetch after each schema/view change.
4. Backfill statuses in small batches.
5. Stop if the connector times out twice in a row.
