# Tracker Fields

Use this schema for the default CSV or table when collecting candidates.

## Required Columns

- `candidate_id`: stable row identifier
- `domain`: apartment, job, partner, vendor, or other
- `source_portal`: where the listing was found
- `entity_name`: listing title, company name, profile name, or equivalent
- `listing_url`: page where the candidate was discovered
- `action_url`: page where the next meaningful action happens
- `status`: one of `found`, `shortlisted`, `action-found`, `waiting-human`, `completed`, `skipped`
- `fit_label`: `high`, `medium`, or `low`
- `hard_match_summary`: which must-have rules are satisfied or missing
- `soft_match_summary`: which preferences are satisfied
- `blockers`: login, CAPTCHA, OTP, missing documents, paywall, unknown
- `next_step`: the next action for AI or human
- `notes`: short free-text evidence
- `last_checked_at`: ISO date or timestamp

## Optional Columns

- `location`
- `price_or_salary`
- `size_or_seniority`
- `availability_date`
- `distance_metric`
- `contact_name`
- `account_required`
- `documents_required`
- `source_confidence`

## Recording Rules

- Keep URLs in separate columns for discovery and action pages.
- Prefer normalized facts over long notes.
- Mark unknown values as `unknown` rather than leaving them ambiguous.
- Update `status` whenever the workflow changes state.
- Record blockers immediately so the user can see why progress paused.
- Keep summaries short enough to scan in a spreadsheet.

## Handoff Rule

Do not present a candidate as ready unless `listing_url`, `action_url`, `fit_label`, `blockers`, and `next_step` are filled in.
