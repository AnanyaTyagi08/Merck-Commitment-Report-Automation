import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.transforms import filter_grt_spmt_report, filter_overdue_and_six_months, populate_working_due_date


@pytest.mark.skip(reason="Pending transformation logic implementation")
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


@pytest.mark.skip(reason="Pending transformation logic implementation")
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


@pytest.mark.skip(reason="Pending transformation logic implementation")
def test_working_due_date_fallback():
    """Verify Working Due Date copies from Commitment Due Date when blank."""
    raw_data = pd.DataFrame({
        "Commitment Due Date": [pd.Timestamp("2026-11-01"), pd.Timestamp("2026-12-01")],
        "Working Due Date": [None, pd.Timestamp("2026-12-15")]
    })
    
    result = populate_working_due_date(raw_data)
    assert result.loc[0, "Working Due Date"] == pd.Timestamp("2026-11-01")
    assert result.loc[1, "Working Due Date"] == pd.Timestamp("2026-12-15")