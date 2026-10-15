"""Create dummy data to visually check TASK-9 formatting."""

from pathlib import Path

from openpyxl import Workbook

from src.excel_generator import apply_font_color, apply_sheet_layout


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Formatting Preview"

    ws.append(["Dummy data - formatting demonstration only"])
    ws.append(["Commitment ID", "Metric Indicator", "Working Due Date"])

    for number in range(1, 51):
        ws.append([f"TEST-{number:03}", "Green", "2026-10-01"])

    ws["B3"] = "Red"
    ws["B4"] = "Purple"

    apply_sheet_layout(ws, header_row=2)
    apply_font_color(ws, ["B3", "C3"], "red")
    apply_font_color(ws, ["B4", "C4"], "purple")

    ws.column_dimensions["A"].width = 55
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 24

    output_dir = Path("resources")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "task9_formatting_preview.xlsx"

    wb.save(output_path)
    wb.close()
    print(f"Created: {output_path.resolve()}")


if __name__ == "__main__":
    main()