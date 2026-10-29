"""Data transformation and business logic for Merck Commitment Reports."""

import pandas as pd


def filter_grt_spmt_report(df: pd.DataFrame) -> pd.DataFrame:
    """Filter records for GRT / SPMT reports per RPP-200-ER03 rules."""
    not_completed = df["Commitment Lifecycle State"].ne("Completed")
    submitted_outside_us = (
        df["Completed State Qualifier"].eq("Submitted")
        & ~df["Country Name"].isin(
    ["United States", "United States of America"]
)
    )

    return df.loc[not_completed & ~submitted_outside_us].copy()


def filter_overdue_and_six_months(df: pd.DataFrame) -> pd.DataFrame:
    """Filter records overdue or due within the next six months."""
    raise NotImplementedError("Pending implementation")


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

def filter_keytruda_report(
    df: pd.DataFrame,
    report_date: pd.Timestamp,
) -> pd.DataFrame:
    """Filter Keytruda commitments per SOP Section 3.3."""
    df = populate_working_due_date(df)
    df = filter_grt_spmt_report(df)

    product = (
        df["Primary Product Family"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )
    df = df.loc[product.eq("pembrolizumab").fillna(False)].copy()

    due_dates = pd.to_datetime(
        df["Working Due Date"], errors="coerce"
    )
    report_month = pd.Timestamp(report_date).to_period("M")
    cutoff = (report_month + 5).end_time.normalize()

    within_window = due_dates.dt.normalize().le(cutoff)
    placeholder = due_dates.dt.year.isin([2098, 2099])

    df["Working Due Date"] = due_dates
    df = df.loc[within_window | placeholder].copy()

    return (
        df.sort_values("Working Due Date", kind="stable")
        .reset_index(drop=True)
    )
