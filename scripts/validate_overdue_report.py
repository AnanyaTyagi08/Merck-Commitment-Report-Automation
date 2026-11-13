"""Compare a generated Overdue/6-Months workbook with a sponsor baseline."""

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook


def file_hash(path):
    """Identify the exact workbook used for validation."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value):
    """Normalize empty cells and dates without changing source files."""
    if value is None or value == "":
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def inspect_workbook(path, sheet_name):
    """Read report data and selected workbook formatting."""
    workbook = load_workbook(path, data_only=True)
    try:
        #falling back to active sheet if the specified name isn't found
        sheet = workbook[sheet_name] if sheet_name in workbook.sheetnames else workbook.active

        #dynamically detecting if headers are on Row 1 or Row 2
        row_1_vals = [cell.value for cell in sheet[1]]
        row_2_vals = [cell.value for cell in sheet[2]]

        if "Working Due Date" in row_1_vals:
            headers = row_1_vals
            data_start_row = 2
        elif "Working Due Date" in row_2_vals:
            headers = row_2_vals
            data_start_row = 3
        else:
            raise ValueError(
                f"Could not find 'Working Due Date' header in {path.name}.\n"
                f"Row 1: {row_1_vals}\nRow 2: {row_2_vals}"
            )

        headers = ["MK/V #" if h == "D/S #" else h for h in headers]

        rows = [
            tuple(row)
            for row in sheet.iter_rows(min_row=data_start_row, values_only=True)
            if any(value is not None for value in row)
        ]

        date_index = headers.index("Working Due Date")
        state_index = headers.index("Commitment Lifecycle State")

        dates = [row[date_index] for row in rows if isinstance(row[date_index], datetime)]

        summary = {
            "filename": path.name,
            "sha256": file_hash(path),
            "worksheets": workbook.sheetnames,
            "records": len(rows),
            "columns": len(headers),
            "freeze_panes": sheet.freeze_panes,
            "auto_filter": sheet.auto_filter.ref if sheet.auto_filter else None,
            #checking bolding on the detected header row
            "all_headers_bold": all(
                sheet.cell(data_start_row - 1, column).font.bold
                for column in range(1, len(headers) + 1)
            ),
            "lifecycle_states": dict(Counter(str(row[state_index]) for row in rows)),
            "missing_or_invalid_dates": len(rows) - len(dates),
            "dates_sorted_ascending": dates == sorted(dates),
            "due_date_months": dict(
                sorted(Counter(value.strftime("%Y-%m") for value in dates).items())
            ),
        }
        return headers, rows, summary
    finally:
        workbook.close()


def compare_rows(generated_rows, baseline_rows):
    """Compare row multisets, excluding unreliable cross-file IDs."""
    #slicing from [1:] to skip column A (Commitment ID) just like the Keytruda test
    generated = Counter(tuple(normalize(value) for value in row[1:]) for row in generated_rows)
    baseline = Counter(tuple(normalize(value) for value in row[1:]) for row in baseline_rows)

    return {
        "comparison": "Exact values across columns B onward; IDs excluded",
        "exact_matching_rows": sum((generated & baseline).values()),
        "generated_only_rows": sum((generated - baseline).values()),
        "baseline_only_rows": sum((baseline - generated).values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sheet", default="Sheet1")
    args = parser.parse_args()

    for path in (args.generated, args.baseline):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    generated_headers, generated_rows, generated_summary = inspect_workbook(
        args.generated, args.sheet
    )
    baseline_headers, baseline_rows, baseline_summary = inspect_workbook(args.baseline, args.sheet)

    if generated_headers[1:] != baseline_headers[1:]:
        print("\n--- HEADER MISMATCH DETAILS ---")
        #comparing columns side-by-side
        for i, (g_col, b_col) in enumerate(
            zip(generated_headers[1:], baseline_headers[1:]), start=2
        ):
            if g_col != b_col:
                print(f"Column {i} -> Generated: '{g_col}' | Baseline: '{b_col}'")

        #checking if one file has more columns than the other
        if len(generated_headers) != len(baseline_headers):
            print(
                f"\nTotal Columns -> Generated: {len(generated_headers)} | "
                f"Baseline: {len(baseline_headers)}"
            )

        parser.error("Columns B onward do not align. Review headers before comparing.")

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    result = {
        "code_commit": commit,
        "generated": generated_summary,
        "baseline": baseline_summary,
        "row_comparison": compare_rows(generated_rows, baseline_rows),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result["row_comparison"], indent=2))
    print(f"Results saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
