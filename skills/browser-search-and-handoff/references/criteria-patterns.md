# Criteria Patterns

Use this file when the user has not fully specified what they want to search for.

## Shared Model

Normalize the request into the same shape across domains:

- `target_type`: what kind of entity to find
- `hard_constraints`: must-have rules
- `soft_preferences`: ranking boosts
- `exclusions`: deal-breakers
- `search_scope`: portals, cities, distance radius, or geography
- `time_window`: move-in date, start date, response urgency, or availability
- `action_goal`: shortlist, contact, apply, register, or draft outreach
- `safe_profile_fields`: facts that may be reused in forms
- `human_only_steps`: what the user wants to handle personally
- `stop_condition`: target result count or review threshold

If several of these are missing, ask compact follow-up questions before browsing.

## Apartment Search

Common fields:

- Location or neighborhoods
- Maximum commute or distance from a reference point
- Budget range
- Number of rooms
- Minimum square meters
- Earliest move-in date
- Furnished or unfurnished
- Student-only or non-student restriction
- Wi-Fi quality requirement
- Distance to train station
- Distance to supermarket
- Pets, smoking, or accessibility requirements

Useful follow-up prompts:

- "Which locations are acceptable, and which are not?"
- "What is the maximum monthly cost including fees?"
- "Is commute time a hard limit or just a preference?"
- "What move-in window is acceptable?"
- "Should I exclude student-only offers?"

## Job Search

Common fields:

- Target job titles
- Seniority level
- Required skills and stack
- Salary floor or range
- Remote, hybrid, or onsite preference
- Location and visa or work-authorization limits
- Industry preferences
- Company size preferences
- Employment type: full-time, contract, internship
- Start-date constraints
- Required documents: CV, cover letter, portfolio

Useful follow-up prompts:

- "Which titles should count as close matches?"
- "What compensation floor should I enforce?"
- "Are remote roles acceptable across time zones?"
- "Which skills are mandatory versus nice to have?"
- "Do you want me to look for easy-apply flows only, or also company sites?"

## Partner Search

Use extra caution. Keep the workflow authentic and under clear user control.

Common fields:

- Geography or search radius
- Age range
- Relationship goal
- Languages
- Lifestyle preferences
- Religion or value-based preferences
- Family goals
- Deal-breakers
- Interests or compatibility signals
- Whether the user wants only profile discovery or also draft openers

Useful follow-up prompts:

- "What are your hard deal-breakers?"
- "Do you want long-term compatibility filters or broader discovery?"
- "Should I only collect profiles, or also draft message options?"
- "Which parts of your own profile are safe to reuse?"

Do not send messages or take persona-defining actions without explicit user confirmation.

## General Follow-Up Pattern

When criteria are incomplete, ask for:

1. The hard filters
2. The ranking preferences
3. The allowed portals or regions
4. The desired output format
5. The steps the human wants to keep manual
