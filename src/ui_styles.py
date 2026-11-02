"""Custom styling and upload display helpers for the Streamlit UI."""

#Merck teal for all action buttons, with a darker shade for hover/click
CUSTOM_CSS = """
<style>
button[kind="primary"],
div[data-testid="stDownloadButton"] button {
    background-color: #00857C;
    border-color: #00857C;
    color: white;
}
button[kind="primary"]:hover,
button[kind="primary"]:focus,
button[kind="primary"]:active,
div[data-testid="stDownloadButton"] button:hover,
div[data-testid="stDownloadButton"] button:focus,
div[data-testid="stDownloadButton"] button:active {
    background-color: #006B63;
    border-color: #006B63;
    color: white;
}
button[kind="primary"]:disabled {
    background-color: #00857C;
    border-color: #00857C;
    color: white;
    opacity: 0.5;
}
</style>
"""


def format_file_size(num_bytes: int) -> str:
    """Turn a file size in bytes into an easy-to-read string like '2.0 KB'."""
    if num_bytes < 1000:
        return f"{num_bytes} B"
    if num_bytes < 1000 * 1000:
        return f"{num_bytes / 1000:.1f} KB"
    return f"{num_bytes / (1000 * 1000):.1f} MB"
