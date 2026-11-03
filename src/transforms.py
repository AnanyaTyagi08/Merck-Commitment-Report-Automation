"""Data transformation and business logic for Merck Commitment Reports."""

import warnings

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
    df = df.copy()
    df["Working Due Date"] = df["Working Due Date"].fillna(
        df["Commitment Due Date"]
    )
    return df


def filter_three_year_lookback(
    df: pd.DataFrame,
    today: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Keep records with Working Due Date in the last three years."""
    df = df.copy()
    df["Working Due Date"] = pd.to_datetime(
        df["Working Due Date"],
        errors="coerce",
    )

    if today is None:
        today = pd.Timestamp.today()

    cutoff = today.normalize() - pd.DateOffset(years=3)
    df = df.loc[df["Working Due Date"] >= cutoff]

    return df.sort_values("Working Due Date").reset_index(drop=True)


def filter_keytruda_report(
    df: pd.DataFrame,
    report_date: pd.Timestamp,
) -> pd.DataFrame:
    """Filter Keytruda commitments per SOP Section 3.3.

    Current interpretation, pending sponsor confirmation:
    include overdue records and dates through the end of the report
    month plus five following months. Also retain years 2098 and 2099.

    Warn about relevant records excluded because their due date remains
    missing or invalid after applying the existing due-date fallback.
    """
    df = populate_working_due_date(df)
    df = filter_grt_spmt_report(df)

    product = (
        df["Primary Product Family"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    df = df.loc[product.eq("pembrolizumab").fillna(False)].copy()

    raw_due_dates = df["Working Due Date"]
    due_dates = pd.to_datetime(raw_due_dates, errors="coerce")

    missing_dates = (
        raw_due_dates.isna()
        | raw_due_dates.astype("string").str.strip().eq("").fillna(False)
    )
    invalid_dates = due_dates.isna() & ~missing_dates

    missing_count = int(missing_dates.sum())
    invalid_count = int(invalid_dates.sum())

    if missing_count or invalid_count:
        warnings.warn(
            "Keytruda report excluded records with unusable due dates: "
            f"{missing_count} missing and {invalid_count} invalid.",
            UserWarning,
            stacklevel=2,
        )

    report_month = pd.Timestamp(report_date).to_period("M")
    cutoff = (report_month + 5).end_time.normalize()

    # No lower boundary: overdue records are included.
    within_window = due_dates.dt.normalize().le(cutoff)

    # These years represent commitments without an established due date.
    placeholder_dates = due_dates.dt.year.isin([2098, 2099])

    df["Working Due Date"] = due_dates
    df = df.loc[within_window | placeholder_dates].copy()

    return df.sort_values(
        "Working Due Date",
        kind="stable",
    ).reset_index(drop=True)
