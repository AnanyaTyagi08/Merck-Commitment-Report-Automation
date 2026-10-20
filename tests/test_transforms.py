
import io

import pandas as pd

from src.transforms import (
    filter_grt_spmt_report,
    populate_working_due_date,
)


def test_completed_commitments_removal():
    """Ensure completed records are stripped out completely (RPP-200-ER03 Section 3.1.2)."""
    raw_data = pd.DataFrame({
        "Commitment Lifecycle State": ["Completed", "Active", "Ongoing"],
        "Completed State Qualifier": ["Submitted", None, None],
        "Country Name": ["United States", "United States", "France"],
        "Working Due Date": [pd.Timestamp.now()] * 3
    })

    cleaned = filter_grt_spmt_report(raw_data)
    assert "Completed" not in cleaned["Commitment Lifecycle State"].values


def test_country_filter_for_submitted_state():
    """Ensure only US records remain if Completed State Qualifier is 'Submitted'."""
    raw_data = pd.DataFrame({
        "Commitment Lifecycle State": ["Active", "Active"],
        "Completed State Qualifier": ["Submitted", "Submitted"],
        "Country Name": ["United States", "France"],
        "Working Due Date": [pd.Timestamp.now()] * 2
    })

    cleaned = filter_grt_spmt_report(raw_data)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Country Name"] == "United States"


def test_non_submitted_non_us_records_are_retained():
    """Ensure the country restriction only applies to records marked Submitted."""
    raw_data = pd.DataFrame({
        "Commitment Lifecycle State": ["Active", "Active", "Completed"],
        "Completed State Qualifier": ["Pending", "Submitted", "Pending"],
        "Country Name": ["France", "France", "France"],
        "Working Due Date": [pd.Timestamp.now()] * 3,
    })

    cleaned = filter_grt_spmt_report(raw_data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Completed State Qualifier"] == "Pending"
    assert cleaned.iloc[0]["Country Name"] == "France"


#date population unit tests
def test_working_due_date_fallback():
    """Verify Working Due Date copies from Commitment Due Date when blank."""
    raw_data = pd.DataFrame({
        "Commitment Due Date": [pd.Timestamp("2026-11-01"), pd.Timestamp("2026-12-01")],
        "Working Due Date": [None, pd.Timestamp("2026-12-15")]
    })

    result = populate_working_due_date(raw_data)
    assert result.loc[0, "Working Due Date"] == pd.Timestamp("2026-11-01")
    assert result.loc[1, "Working Due Date"] == pd.Timestamp("2026-12-15")


#verifying ingestion logic
def test_integration_excel_ingestion_and_date_population():
    """Verify Excel ingestion logic (sheet='Export', header=1) works with the date fallback."""
    #creating mock DataFrame simulating the VReg export structure
    mock_data = pd.DataFrame({
        "Commitment ID": ["A01", "A02"],
        "Commitment Due Date": [pd.Timestamp("2026-11-01"), pd.Timestamp("2026-12-01")],
        "Working Due Date": [None, pd.Timestamp("2026-12-15")],
    })

    #simulating the VReg excel format: Coverpage, then Export sheet with a junk header row
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Cover": ["Page"]}).to_excel(
            writer, sheet_name="Coverpage", index=False
        )
        export_sheet = writer.book.create_sheet("Export")
        export_sheet.append(["Junk Row", "Ignore Me"])
        export_sheet.append(list(mock_data.columns))
        for _, row in mock_data.iterrows():
            export_sheet.append(list(row))

    buffer.seek(0)

    #reading 'Export' sheet, skipping the first row (header=1)
    ingested_df = pd.read_excel(buffer, sheet_name="Export", header=1)

    #applying date population transformation
    cleaned_df = populate_working_due_date(ingested_df)

    #verifying the blank date was populated correctly
    assert cleaned_df.loc[0, "Working Due Date"] == pd.Timestamp("2026-11-01")
    assert cleaned_df.loc[1, "Working Due Date"] == pd.Timestamp("2026-12-15")


#creating mock Excel export data for ingestion tests
def create_mock_export_workbook() -> io.BytesIO:
    #creating mock DataFrame simulating the VReg export structure
    mock_data = pd.DataFrame({
        "Commitment ID": ["A01", "A02", "A03", "A04"],
        "Commitment Due Date": [
            pd.Timestamp("2026-11-01"),
            pd.Timestamp("2026-12-01"),
            pd.Timestamp("2026-10-15"),
            pd.Timestamp("2026-09-01"),
        ],
        "Working Due Date": [None, pd.Timestamp("2026-12-15"), None, None],
        "Commitment Lifecycle State": ["Active", "Active", "Completed", "Active"],
        "Completed State Qualifier": ["Pending", "Submitted", "Submitted", "Submitted"],
        "Country Name": ["France", "United States", "United States", "France"],
    })

    #simulating the VReg excel format: Coverpage, then Export sheet with a junk header row
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Cover": ["Page"]}).to_excel(
            writer, sheet_name="Coverpage", index=False
        )
        export_sheet = writer.book.create_sheet("Export")
        export_sheet.append(["Junk Row", "Ignore Me"])
        export_sheet.append(list(mock_data.columns))
        for _, row in mock_data.iterrows():
            export_sheet.append(list(row))

    buffer.seek(0)
    return buffer


#combined Excel ingestion and transformation test
def test_combined_excel_ingestion_and_transformations():
    """Verify ingestion applies date population and report filtering."""
    buffer = create_mock_export_workbook()

    #reading 'Export' sheet, skipping the first row (header=1)
    ingested_df = pd.read_excel(buffer, sheet_name="Export", header=1)

    #applying transformations in the same order as the application
    cleaned_df = populate_working_due_date(ingested_df)
    cleaned_df = filter_grt_spmt_report(cleaned_df)

    #verifying the blank date was populated and excluded rows were filtered
    assert cleaned_df["Commitment ID"].tolist() == ["A01", "A02"]
    assert cleaned_df.loc[cleaned_df["Commitment ID"] == "A01", "Working Due Date"].iloc[0] == (
        pd.Timestamp("2026-11-01")
    )
    assert cleaned_df.loc[cleaned_df["Commitment ID"] == "A02", "Working Due Date"].iloc[0] == (
        pd.Timestamp("2026-12-15")
    )
