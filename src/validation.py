"""Checks that an uploaded commitment export has what the report needs."""

import pandas as pd

#columns the report pipeline reads from the VReg export
REQUIRED_COLUMNS = [
    "Commitment Due Date",
    "Working Due Date",
    "Commitment Lifecycle State",
    "Completed State Qualifier",
    "Country Name",
    "Primary Product Family",

]


def find_missing_columns(df: pd.DataFrame) -> list[str]:
    """Return the required columns that are not in the uploaded file."""
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def missing_columns_message(missing: list[str]) -> str:
    """Build a user-friendly warning listing the missing columns."""
    column_list = "\n".join(f"- {col}" for col in missing)
    return (
        "The uploaded file is missing required columns:\n\n"
        f"{column_list}\n\n"
        "Please re-export the VQ - Commitment Query report with all columns "
        "and upload it again."
    )
