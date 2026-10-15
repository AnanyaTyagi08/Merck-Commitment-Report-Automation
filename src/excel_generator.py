"""Excel report generator for Merck Commitment Reports."""

from copy import copy
from pathlib import Path
from typing import Union

import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def apply_sheet_layout(
    ws: Worksheet,
    header_row: int = 1,
) -> None:
    """Freeze rows through the header and enable column filters."""
    if header_row < 1 or header_row > ws.max_row:
        raise ValueError("Header row must exist in the worksheet.")

    ws.freeze_panes = f"A{header_row + 1}"

    last_column = get_column_letter(ws.max_column)
    ws.auto_filter.ref = (
        f"A{header_row}:{last_column}{ws.max_row}"
    )

def apply_font_color(
    ws: Worksheet,
    cell_addresses: list[str],
    color: str,
) -> None:
    """Color specified cells red or purple, preserving other font settings."""
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
