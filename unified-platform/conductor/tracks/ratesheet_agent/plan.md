# Rate Sheet Agent Track

## Objective
Automate the ingestion, parsing, and structured storage of lender rate sheets.

## Workflows
1. **Ingestion**: Monitor email/folder -> Parse PDF (Claude Vision) -> Staging DB.
2. **Validation**: "Diff View" Dashboard for human review.
3. **Sync**: Publish validated rates to Live Pricing Engine.

## Current Status
- [ ] Port Parser Logic from `custompricing`
- [ ] Implement `RateSheet` Staging Model
- [ ] Implement `RateProgram` Staging Model
