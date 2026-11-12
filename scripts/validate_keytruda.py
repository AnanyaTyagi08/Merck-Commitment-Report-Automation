"""Compare a generated Keytruda workbook with a sponsor baseline."""

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
        sheet = workbook[sheet_name]
        headers = [cell.value for cell in sheet[2]]
        rows = [
            tuple(row)
            for row in sheet.iter_rows(min_row=3, values_only=True)
            if any(value is not None for value in row)
        ]

        date_index = headers.index("Working Due Date")
        state_index = headers.index("Commitment Lifecycle State")
        product_index = headers.index("Primary Product Family")
        qualifier_index = headers.index("Completed State Qualifier")
        country_index = headers.index("Country Name")

        dates = [
            row[date_index]
            for row in rows
            if isinstance(row[date_index], datetime)
        ]

        summary = {
            "filename": path.name,
            "sha256": file_hash(path),
            "worksheets": workbook.sheetnames,
            "records": len(rows),
            "columns": len(headers),
            "freeze_panes": sheet.freeze_panes,
            "auto_filter": sheet.auto_filter.ref,
            "all_headers_bold": all(
                sheet.cell(2, column).font.bold
                for column in range(1, len(headers) + 1)
            ),
            "working_due_date_formats": dict(Counter(
                sheet.cell(row_number, date_index + 1).number_format
                for row_number in range(3, sheet.max_row + 1)
                if any(
                    cell.value is not None
                    for cell in sheet[row_number]
                )
            )),
            "lifecycle_states": dict(Counter(
                str(row[state_index]) for row in rows
            )),
            "product_families": dict(Counter(
                str(row[product_index]) for row in rows
            )),
            "missing_or_invalid_dates": len(rows) - len(dates),
            "dates_sorted_ascending": dates == sorted(dates),
            "due_date_months": dict(sorted(Counter(
                value.strftime("%Y-%m") for value in dates
            ).items())),
            "non_us_submitted_qualifier_records": sum(
                row[qualifier_index] == "Submitted"
                and row[country_index] not in {
                    "United States",
                    "United States of America",
                }
                for row in rows
            ),
        }
        return headers, rows, summary
    finally:
        workbook.close()


def compare_rows(generated_rows, baseline_rows):
    """Compare row multisets, excluding unreliable cross-file IDs."""
    generated = Counter(
        tuple(normalize(value) for value in row[1:])
        for row in generated_rows
    )
    baseline = Counter(
        tuple(normalize(value) for value in row[1:])
        for row in baseline_rows
    )

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
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--report-date", required=True, type=date.fromisoformat)
    parser.add_argument("--sheet", default="Keytruda Sep 2026")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    for path in (args.generated, args.baseline, args.source):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    inputs = {
        path.resolve()
        for path in (args.generated, args.baseline, args.source)
    }
    if args.output.resolve() in inputs:
        parser.error("Output must not overwrite an input workbook.")

    generated_headers, generated_rows, generated_summary = inspect_workbook(
        args.generated, args.sheet
    )
    baseline_headers, baseline_rows, baseline_summary = inspect_workbook(
        args.baseline, args.sheet
    )

    # The baseline's first header is blank. Compare remaining columns by name.
    if generated_headers[1:] != baseline_headers[1:]:
        parser.error(
            "Columns B onward do not align. Review headers before comparing."
        )

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    result = {
        "code_commit": commit,
        "report_date": args.report_date.isoformat(),
        "source": {
            "filename": args.source.name,
            "sha256": file_hash(args.source),
        },
        "generated": generated_summary,
        "baseline": baseline_summary,
        "header_differences": [
            {
                "column": index,
                "generated": generated,
                "baseline": baseline,
            }
            for index, (generated, baseline) in enumerate(
                zip(generated_headers, baseline_headers),
                start=1,
            )
            if generated != baseline
        ],
        "row_comparison": compare_rows(generated_rows, baseline_rows),
        "limitations": [
            "Raw export date: 2026-10-02; baseline export date: 2026-09-01.",
            "Commitment IDs are not established as stable across these files.",
            "The six-month boundary remains pending confirmation.",
            "Differences are observations, not automatically code defects.",
            "Formatting checks are partial; visual review is still required.",
        ],
        "conclusion": "Full baseline parity not established.",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(result["row_comparison"], indent=2))
    print(result["conclusion"])
    print(f"Results saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
