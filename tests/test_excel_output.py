import openpyxl
import pandas as pd
import pytest

from src.excel_generator import build_grt_spmt_workbook


#skipped purposefully: out of scope for Task-6. excel workbook formatting
#(Red-Late/Purple-Pending tabs) will be handled in a separate epic/ticket
@pytest.mark.skip(reason="Pending excel generator implementation")
def test_required_workbook_tabs_and_freeze_panes(tmp_path):
    """Verify workbook generates Red-Late and Purple-Pending tabs with frozen headers."""
    sample_df = pd.DataFrame({
        "Commitment Lifecycle State": ["Ongoing"],
        "Metric Indicator": ["Purple"],
        "Working Due Date": [pd.Timestamp.now() - pd.Timedelta(days=10)],
        "Country Name": ["United States"]
    })

    output_path = tmp_path / "test_report.xlsx"
    build_grt_spmt_workbook(sample_df, output_path)

    wb = openpyxl.load_workbook(output_path)
    sheet_names = wb.sheetnames

    #asserting expected sheets exist per RPP-200-ER03
    assert "Red-Late" in sheet_names
    assert "Purple-Pending" in sheet_names

    #verifying top row is frozen on main sheet
    ws = wb.active
    assert ws.freeze_panes == "A2"
