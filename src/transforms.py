"""Data transformation and business logic for Merck Commitment Reports."""

import pandas as pd


def filter_grt_spmt_report(df: pd.DataFrame) -> pd.DataFrame:
    """Filter records for GRT / SPMT reports per RPP-200-ER03 rules."""
    not_completed = df["Commitment Lifecycle State"].ne("Completed")
    submitted_outside_us = (
        df["Completed State Qualifier"].eq("Submitted")
        & df["Country Name"].ne("United States")
    )

    return df.loc[not_completed & ~submitted_outside_us].copy()


def filter_overdue_and_six_months(df: pd.DataFrame) -> pd.DataFrame:
    """Filter records overdue or due within the next six months."""
    raise NotImplementedError("Pending implementation")


def populate_working_due_date(df: pd.DataFrame) -> pd.DataFrame:
    """Populate Working Due Date from Commitment Due Date if missing."""
    raise NotImplementedError("Pending implementation")
