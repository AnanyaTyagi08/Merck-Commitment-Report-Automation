"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import streamlit as st


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Merck Commitment Report Automation",
        layout="wide",
    )
    st.title("Merck Commitment Report Automation")
    st.write("Upload raw commitment reports to automate filtering and formatting.")


if __name__ == "__main__":
    main()

