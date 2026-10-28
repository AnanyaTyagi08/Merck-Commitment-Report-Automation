"""Dynamic filenames for monthly commitment reports."""

from datetime import date, timedelta
from typing import TypedDict

MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)

class ReportFilenames(TypedDict):
    """Filename keys shared by report generation callers."""
    grt_spmt: str
    overdue_and_six_months: str
    keytruda_ongoing: str
    new_pv: str

def get_report_filenames(today: date | None = None) -> ReportFilenames:
    """Return report filenames using today's date unless a date is supplied."""
    # Pass today explicitly for deterministic tests or scheduled report dates.
    if today is None:
        today = date.today()
    month_year = f"{MONTHS[today.month - 1]}{today.year:04d}"
    # New PV range: first day of the previous month through today.
    first_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    start = (
        f"{first_last_month.day:02d}-{MONTHS[first_last_month.month - 1]}-"
        f"{first_last_month.year:04d}"
    )
    end = f"{today.day:02d}-{MONTHS[today.month - 1]}-{today.year:04d}"
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
