# Task 19: Keytruda baseline validation

## Scope

Compare the generated September 2026 Keytruda workbook against the
sponsor-provided sample. Report date: 2026-09-01.

Validation code: scripts/validate_keytruda.py.
Local results: resources/task19_validation/validation_results.json.
The results JSON records the code commit and input-file SHA-256 hashes.

## Inputs

- Raw: Sample raw data Commitments Report-Keytruda-Ongoing-01Sep26.xlsx
- Baseline: Sample Commitments Report-Keytruda-Ongoing-01Sep26 (1).xlsx
- Generated: Commitments Report-Keytruda-Ongoing-Sep2026.xlsx

## Data comparison

| Check | Generated | Baseline |
|---|---|---|
| Records | 103 | 87 |
| Columns | 30 | 30 |
| Product family | Pembrolizumab only | Pembrolizumab only |
| Completed lifecycle records | 0 | 0 |
| Missing or invalid Working Due Dates | 0 | 0 |
| Working Due Dates sorted ascending | Yes | Yes |
| Lifecycle states | 81 Ongoing, 22 Submitted | 85 Ongoing, 2 Submitted |

Exact multiset comparison across the 29 columns after Commitment ID:
82 matching rows, 21 generated-only rows, and 5 baseline-only rows.
Empty cells were normalized. IDs were excluded because cross-file
record identity has not been established.

All 16 generated records with Completed State Qualifier = Submitted
have Country Name = United States of America. No non-US records with
that qualifier appear in this output.

## Workbook comparison

- Both report worksheets freeze panes at A3.
- Both auto-filter ranges cover their respective report datasets.
- Headers B through AD match. Generated A2 is Commitment ID;
  baseline A2 is blank.
- The baseline includes a Coverpage; the generated workbook does not.
- Generated Working Due Date format: YYYY-MM-DD HH:MM:SS.
  Baseline format: dd-mmm-yyyy.
- Not all generated headers are bold; all baseline headers are bold.
- Column widths differ.
- Direct font-color encodings differ. This alone does not establish
  a visible color mismatch.
- Neither report worksheet contains conditional-formatting rules.

## Limitations and open questions

- The raw export ran on 2026-10-02; the baseline export ran on
  2026-09-01. They are different source snapshots.
- Matching Commitment IDs cannot be assumed to identify the same
  records across these files.
- Sponsor confirmation of the six-month boundary and inclusion of
  all overdue records remains pending.
- The shared GRT/SPMT filter retains all Ongoing records regardless
  of country and qualifier. Its suitability for Keytruda needs
  review, although this dataset contains no non-US Submitted-
  qualifier records in the generated output.
- Differences have not been fully attributed to snapshot changes,
  anonymization, or implementation behavior.
- Visual review and independent teammate review remain pending.

## Conclusion

Full baseline parity is not established. Selected data and layout
checks match, but record differences and formatting differences
remain. Report-generation logic was not changed during validation.

These findings support Task 21; they are not a final parity sign-off.

### Manual Excel review

- Column headers are readable.
- Generated dates display unnecessary time components.
- Content is cut off in columns H, I, P, Q, R, T, AA, AB, and AC.
- Frozen headers and column filters work correctly.

Date formatting and column widths need follow-up.
Full baseline parity remains unconfirmed because of the documented
record differences and different source snapshot dates.