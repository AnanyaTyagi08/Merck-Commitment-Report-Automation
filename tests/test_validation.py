import pandas as pd

from src.validation import (
    REQUIRED_COLUMNS,
    find_missing_columns,
    missing_columns_message,
)


#verifying a complete file passes the column check (TASK-18)
def test_no_missing_columns():
    """A file with every required column has nothing missing."""
    df = pd.DataFrame(columns=REQUIRED_COLUMNS + ["Commitment ID"])
    assert find_missing_columns(df) == []


#verifying missing columns are found and listed in order
def test_missing_columns_are_found():
    """Columns that are not in the file are returned."""
    df = pd.DataFrame(columns=["Commitment Due Date", "Country Name"])
    assert find_missing_columns(df) == [
        "Working Due Date",
        "Commitment Lifecycle State",
        "Completed State Qualifier",
        "Primary Product Family",

    ]


#verifying the warning names each missing column
def test_missing_columns_message_lists_columns():
    """The warning text includes every missing column."""
    message = missing_columns_message(["Country Name", "Working Due Date"])
    assert "- Country Name" in message
    assert "- Working Due Date" in message
    assert "re-export" in message
