"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import io

import pandas as pd
import streamlit as st

from src.transforms import (
    filter_grt_spmt_report,
    filter_three_year_lookback,
    populate_working_due_date,
)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Merck Commitment Report Automation",
        layout="wide",
    )
    st.title("Merck Commitment Report Automation")
    st.write("Upload raw commitment reports to automate filtering and formatting.")
    st.markdown(
        """
        <style>
        button[kind="primary"], button[kind="primary"]:hover,
        button[kind="primary"]:focus, button[kind="primary"]:active {
            background-color: #00857C;
            border-color: #00857C;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload VQ - Commitment Query Excel file", type=["xlsx"])

    if st.button("Generate Report", type="primary", disabled=uploaded_file is None):
        try:
            with st.spinner("Processing spreadsheet..."):
                #reading file and skipping the first sheet and VReg header row
                raw_df = pd.read_excel(uploaded_file, sheet_name='Export', header=1)

                #transformation function executing the date changes
                cleaned_df = populate_working_due_date(raw_df)
                #filter completed commitments and non-US submitted rows
                cleaned_df = filter_grt_spmt_report(cleaned_df)

                #filtering to 3-year lookback and sorting by Working Due Date
                cleaned_df = filter_three_year_lookback(cleaned_df)

                #writing  cleaned dataframe to an in-memory buffer so the user can download it
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    cleaned_df.to_excel(writer, index=False)

            st.success("File processed successfully!")

            #temporary download button to check transformed data
            st.download_button(
                label="Download Cleaned Excel File",
                data=buffer.getvalue(),
                file_name="Cleaned_Commitments.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error processing file: {e}")


if __name__ == "__main__":
    main()
