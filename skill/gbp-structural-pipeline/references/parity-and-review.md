# Parity And Review

## Purpose

Use this reference when comparing the skill to an older workflow, spreadsheet, Revit model, YJK model, or office practice.

## Review Levels

### Engineering-intent parity

The skill reproduces the same structural decision path and governing ideas.

### Data-contract parity

The skill captures the same fields, identifiers, or exchange information needed by the office workflow.

### Software-route parity

The skill preserves the same handoff logic, such as Revit review before solver export.

## Review Workflow

1. identify the artifact being compared
2. identify its actual role in the pipeline
3. locate hidden assumptions and manual steps
4. map those assumptions to the current skill
5. report what should be preserved, removed, or formalized

## Warning Rules

Always call out:
- undocumented manual assumptions
- software-local data that never returns to the source model
- hidden review steps
- brittle one-off scripts
- parity claims that are visual only, not engineering-logical

## Recommended Output

- compared artifact
- parity level achieved
- missing branches
- current skill gaps
- next upgrade with highest leverage
