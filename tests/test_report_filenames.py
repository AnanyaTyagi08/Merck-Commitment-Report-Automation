from datetime import date

from src.report_filenames import get_report_filenames


def test_exact_report_filenames():
    assert get_report_filenames(date(2026, 10, 22)) == {
        "grt_spmt": (
            "Monthly Commitments Report in Support of GRT and SPMT Meetings Oct2026.xlsx"
        ),
        "overdue_and_six_months": (
            "Commitments Overdue and due in the next 6 months-Oct2026.xlsx"
        ),
        "keytruda_ongoing": "Commitments Report-Keytruda-Ongoing-Oct2026.xlsx",
        "new_pv": "Commitments Report-New PV Commitments 01-Sep-2026 to 22-Oct-2026.xlsx",
    }


def test_new_pv_date_range_across_year_boundary():
    assert get_report_filenames(date(2027, 1, 5))["new_pv"] == (
        "Commitments Report-New PV Commitments 01-Dec-2026 to 05-Jan-2027.xlsx"
    )


def test_new_pv_date_range_after_leap_february():
    assert get_report_filenames(date(2028, 3, 1))["new_pv"] == (
        "Commitments Report-New PV Commitments 01-Feb-2028 to 01-Mar-2028.xlsx"
    )
