"""Dynamic filenames for monthly commitment reports."""

from datetime import date, timedelta


def get_report_filenames(today: date | None = None) -> dict[str, str]:
    """Return report filenames using today's date unless a date is supplied."""
    if today is None:
        today = date.today()
    months = (
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    )
    month_year = f"{months[today.month - 1]}{today.year:04d}"
    first_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    start = (
        f"{first_last_month.day:02d}-{months[first_last_month.month - 1]}-"
        f"{first_last_month.year:04d}"
    )
    end = f"{today.day:02d}-{months[today.month - 1]}-{today.year:04d}"
    return {
        "grt_spmt": (
            f"Monthly Commitments Report in Support of GRT and SPMT Meetings {month_year}.xlsx"
        ),
        "overdue_and_six_months": (
            f"Commitments Overdue and due in the next 6 months-{month_year}.xlsx"
        ),
        "keytruda_ongoing": f"Commitments Report-Keytruda-Ongoing-{month_year}.xlsx",
        "new_pv": f"Commitments Report-New PV Commitments {start} to {end}.xlsx",
    }
