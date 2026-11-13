import pandas as pd
import pytest
from openpyxl import Workbook

from src.excel_generator import highlight_overdue_rows
from src.transforms import filter_overdue_and_six_months


@pytest.fixture
def mock_commitments_df():
    """Creates a mock DataFrame mimicking the GRT-SPMT export."""
    today = pd.Timestamp.now().normalize()
    data = {
        "Commitment Lifecycle State": ["Ongoing", "Ongoing", "Ongoing", "Completed", "Ongoing"],
        "Working Due Date": [
            today - pd.Timedelta(days=10),  # overdue (Keep)
            today + pd.Timedelta(days=30),  # upcoming within 6 months (Keep)
            today + pd.Timedelta(days=200),  # > 6 months (Drop)
            today - pd.Timedelta(days=10),  # completed (Drop)
            pd.NaT,  # no date (Drop)
        ],
    }
    return pd.DataFrame(data)


def test_filter_overdue_and_six_months(mock_commitments_df):
    """Verifies the filter isolates Ongoing tasks that are overdue or due within 6 months."""
    result_df = filter_overdue_and_six_months(mock_commitments_df)

    # only rows 0 and 1 should remain
    assert len(result_df) == 2
    assert result_df.index.tolist() == [0, 1]
    assert all(result_df["Commitment Lifecycle State"] == "Ongoing")


def test_highlight_overdue_rows(mock_commitments_df):
    """Verifies that only overdue rows receive the red font formatting."""
    # filtering the df first so it matches the expected input for Report 2
    filtered_df = filter_overdue_and_six_months(mock_commitments_df)

    # creating a mock openpyxl worksheet
    wb = Workbook()
    ws = wb.active

    # writing headers and data to worksheet
    ws.append(list(filtered_df.columns))
    for _, row in filtered_df.iterrows():
        ws.append(list(row))

    # applying the formatting function
    highlight_overdue_rows(ws, filtered_df, header_row=1)

    # the overdue row (index 0) is now on Excel row 2. checking if font is red (FF0000)
    assert ws.cell(row=2, column=2).font.color.rgb == "FFFF0000"

    # the upcoming row (index 1) is on Excel row 3. checking if font is NOT red
    cell_3_color = ws.cell(row=3, column=2).font.color
    if cell_3_color is not None:
        assert cell_3_color.rgb != "FFFF0000"
