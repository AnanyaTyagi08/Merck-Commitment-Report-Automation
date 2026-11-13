# Task 12: Overdue and 6-Months baseline validation

## Scope

Compare the generated November 2026 "Commitments Overdue and due in the next 6 months" workbook against the sponsor-provided September 2026 baseline sample.

Validation code: scripts/validate_overdue_report.py
Local results: resources/task12_validation/validation_results.json
The results JSON records the code commit (623742bf9894bfc3a4bc006e9b384b233a4cb19f) and input-file SHA-256 hashes.

## Inputs

- Baseline: Sample Commitments Overdue and due in the next 6 months-01Sep26.xlsx
- Generated: Commitments Overdue and due in the next 6 months-Nov2026.xlsx

## Data comparison

| Check | Generated | Baseline |
|---|---|---|
| Records | 220 | 181 |
| Columns | 30 | 30 |
| Missing or invalid Working Due Dates | 0 | 0 |
| Working Due Dates sorted ascending | Yes | Yes |
| Lifecycle states | 220 Ongoing | 179 Ongoing, 2 Delayed |

Exact multiset comparison across the 29 columns after Commitment ID:
0 matching rows, 220 generated-only rows, and 181 baseline-only rows. 
Empty cells were normalized, and IDs were excluded because cross-file record identity has not been established. Column 6 header `D/S #` was normalized to `MK/V #` for alignment.

## Workbook comparison

- Generated report freezes panes at A2; baseline has no frozen panes (null).
- Generated auto-filter range is A1:AD221; baseline is A2:AD183.
- Not all generated headers are bold; all baseline headers are bold.
- The baseline workbook contains a "Coverpage" and a "Late" sheet; the generated workbook currently only outputs the main "Ongoing-Upcoming" data sheet.
- The 6-month due date window reflects different starting snapshots. Generated dates span August 2026 to May 2027; baseline dates span August 2026 to February 2027 (with two 2028 outliers).

## Limitations and open questions

- The generated export uses a November 2026 snapshot; the baseline uses a September 2026 snapshot. The temporal shift accounts for the 0 exact row matches.
- The baseline expects `MK/V #` for Column 6, while the generator outputs `D/S #`.
- The current shared status filter retains only `Ongoing` records. The baseline includes `Delayed` records, meaning our status filtering logic for Overdue reports needs revision.
- Differences have not been fully attributed to snapshot changes, anonymization, or implementation behavior.
- Visual review and independent teammate review remain pending.

## Conclusion

Full baseline parity is not established. Zero exact multiset row matches were found due to differing source data snapshots (Sept vs Nov). 

Additionally, formatting differences (bolding, freeze panes) and a strict lifecycle state filter (which dropped `Delayed` records) require remediation.