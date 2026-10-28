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

def filter_overdue_and_six_months(
    df: pd.DataFrame, today: pd.Timestamp | None = None
) -> pd.DataFrame:
    """Filter records overdue or due within the next six months."""
    df = df.copy()
    if today is None:
        today = pd.Timestamp.today()
    today = today.normalize()
    six_months_out = today + pd.DateOffset(months=6)

    #Column L: Ongoing status
    is_ongoing = df["Commitment Lifecycle State"].str.strip() == "Ongoing"
    
    #Column R: Overdue or due within 6 months
    df["Working Due Date"] = pd.to_datetime(df["Working Due Date"], errors="coerce")
    is_overdue_or_upcoming = (df["Working Due Date"] < today) | (
        (df["Working Due Date"] >= today) & (df["Working Due Date"] <= six_months_out)
    )
    
    return df[is_ongoing & is_overdue_or_upcoming].copy()


def populate_working_due_date(df: pd.DataFrame) -> pd.DataFrame:
    """Populate Working Due Date from Commitment Due Date if missing."""
    #creating copy to avoid altering the original dataframe unexpectedly
    df = df.copy()
    df["Working Due Date"] = df["Working Due Date"].fillna(df["Commitment Due Date"])
    return df


def filter_three_year_lookback(
    df: pd.DataFrame, today: pd.Timestamp | None = None
) -> pd.DataFrame:
    """Keep records with Working Due Date in the last 3 years, sorted ascending."""
    #creating copy to avoid altering the original dataframe unexpectedly
    df = df.copy()
    df["Working Due Date"] = pd.to_datetime(df["Working Due Date"], errors="coerce")
    if today is None:
        today = pd.Timestamp.today()
    cutoff = today.normalize() - pd.DateOffset(years=3)
    df = df[df["Working Due Date"] >= cutoff]
    return df.sort_values("Working Due Date").reset_index(drop=True)
