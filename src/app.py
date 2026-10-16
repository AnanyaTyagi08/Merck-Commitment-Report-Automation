"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import pandas as pd
import streamlit as st

from transforms import populate_working_due_date


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Merck Commitment Report Automation",
        layout="wide",
    )
    st.title("Merck Commitment Report Automation")
    st.write("Upload raw commitment reports to automate filtering and formatting.")

    uploaded_file = st.file_uploader("Upload VQ - Commitment Query Excel file", type=["xlsx"])

    if uploaded_file:
        try:
            #reading file and skipping the first sheet and VReg header row
            raw_df = pd.read_excel(uploaded_file, sheet_name='Export', header=1)

            #transformation function executing the date changes
            populate_working_due_date(raw_df)

            st.success("File processed successfully!")

        except Exception as e:
            st.error(f"Error processing file: {e}")


if __name__ == "__main__":
    main()
