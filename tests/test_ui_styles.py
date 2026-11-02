from src.ui_styles import CUSTOM_CSS, format_file_size


#verifying action buttons use Merck teal (TASK-15)
def test_custom_css_uses_merck_teal():
    """Primary and download buttons are styled in Merck teal."""
    assert "#00857C" in CUSTOM_CSS
    assert 'button[kind="primary"]' in CUSTOM_CSS
    assert "stDownloadButton" in CUSTOM_CSS


#verifying file sizes display in readable units
def test_format_file_size():
    """Sizes show as B, KB, or MB."""
    assert format_file_size(500) == "500 B"
    assert format_file_size(2000) == "2.0 KB"
    assert format_file_size(3_000_000) == "3.0 MB"
