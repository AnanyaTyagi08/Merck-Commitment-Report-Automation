"""Excel report generator for Merck Commitment Reports."""

from copy import copy
from pathlib import Path
from typing import Union

import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from src.report_filenames import get_report_filenames


def apply_sheet_layout(
    ws: Worksheet,
    header_row: int = 1,
) -> None:
    """Freeze rows through the header and enable column filters."""
    if header_row < 1 or header_row > ws.max_row:
        raise ValueError("Header row must exist in the worksheet.")

    ws.freeze_panes = f"A{header_row + 1}"

    last_column = get_column_letter(ws.max_column)
    ws.auto_filter.ref = f"A{header_row}:{last_column}{ws.max_row}"


def apply_font_color(
    ws: Worksheet,
    cell_addresses: list[str],
    color: str,
) -> None:
    """Color specified cells while preserving other font settings."""
    colors = {
        "red": "FFFF0000",
        "purple": "FF800080",
    }

    if color not in colors:
        raise ValueError("Color must be 'red' or 'purple'.")

    for address in cell_addresses:
        cell = ws[address]
        updated_font = copy(cell.font)
        updated_font.color = colors[color]
        cell.font = updated_font


def build_grt_spmt_workbook(
    df: pd.DataFrame,
    output_path: Union[str, Path],
) -> None:
    """Generate the formatted Excel workbook with required tabs and views."""
    raise NotImplementedError("Pending implementation")


def build_keytruda_workbook(
    df: pd.DataFrame,
    output_dir: Union[str, Path],
    report_date: pd.Timestamp,
) -> Path:
    """Export a prepared Keytruda report using the report date."""
    report_date = pd.Timestamp(report_date)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = get_report_filenames(
        report_date.date()
    )["keytruda_ongoing"]
    output_path = output_dir / filename

    sheet_name = f"Keytruda {report_date.strftime('%b %Y')}"

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
        date_format="DD-MMM-YYYY",
        datetime_format="DD-MMM-YYYY",
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name,
            startrow=1,
        )

        ws = writer.sheets[sheet_name]
        ws["A1"] = (
            f"Keytruda commitments — "
            f"report date {report_date:%d-%b-%Y}"
        )

        apply_sheet_layout(ws, header_row=2)

        for column_number, column_name in enumerate(df.columns, start=1):
            column_letter = get_column_letter(column_number)
            ws.column_dimensions[column_letter].width = min(
                max(len(str(column_name)) + 3, 18),
                45,
            )

    return output_path
