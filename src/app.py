"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import io

import pandas as pd
import streamlit as st

from src.excel_generator import apply_sheet_layout
from src.report_filenames import get_report_filenames
from src.transforms import (
    filter_grt_spmt_report,
    filter_three_year_lookback,
    populate_working_due_date,
)
from src.ui_styles import CUSTOM_CSS, format_file_size


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Merck Commitment Report Automation",
        layout="wide",
    )
    st.title("Merck Commitment Report Automation")
    st.write("Upload raw commitment reports to automate filtering and formatting.")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload VQ - Commitment Query Excel file", type=["xlsx"])
    if uploaded_file is None:
        st.info("No file uploaded yet.")
    else:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.caption(f"Size: {format_file_size(uploaded_file.size)}")

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
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name="GRT-SPMT")
                    ws = writer.sheets["GRT-SPMT"]
                    apply_sheet_layout(ws, header_row=1)

            st.success("File processed successfully!")


            #temporary download button to check transformed data
            st.download_button(
                label="Download Cleaned Excel File",
                data=buffer.getvalue(),
                file_name=get_report_filenames()["grt_spmt"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error processing file: {e}")


if __name__ == "__main__":
    main()
