"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import io

import pandas as pd
import streamlit as st

from src.excel_generator import highlight_overdue_rows
from src.excel_generator import apply_sheet_layout
from src.report_filenames import get_report_filenames
from src.transforms import (
    filter_grt_spmt_report,
    filter_three_year_lookback,
    populate_working_due_date,
    filter_overdue_and_six_months
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

    #clearing memory if a new file is uploaded
    if uploaded_file and uploaded_file.name != st.session_state.get("last_uploaded_file"):
        st.session_state.clear()
        st.session_state["last_uploaded_file"] = uploaded_file.name
        
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

                #writing cleaned dataframe to an in-memory buffer so the user can download it
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name="GRT-SPMT")
                    ws = writer.sheets["GRT-SPMT"]
                    apply_sheet_layout(ws, header_row=1)
                    
                #ensuring that only Report 2 gets highlighted red rows as per Task-12 requirements
                report_2_df = filter_overdue_and_six_months(cleaned_df)

                buffer_2 = io.BytesIO()
                with pd.ExcelWriter(buffer_2, engine="openpyxl") as writer:
                    report_2_df.to_excel(writer, index=False, sheet_name="Ongoing-Upcoming")
                    ws2 = writer.sheets["Ongoing-Upcoming"]
                    apply_sheet_layout(ws2, header_row=1)
                    highlight_overdue_rows(ws2, report_2_df, header_row=1)
                    
                    #saving to session state so that either download button can be clicked without having to click 'Generate Report' again
                st.session_state["report_1_data"] = buffer.getvalue()
                st.session_state["report_2_data"] = buffer_2.getvalue()

        except Exception as e:
            st.error(f"Error processing file: {e}")
            
        #Modified: Moved outside the button block so they survive reruns
    if "report_1_data" in st.session_state and "report_2_data" in st.session_state:
        st.success("File processed successfully!")

        #Added for TASK-12: Dual Download Buttons
        current_month_year = pd.Timestamp.now().strftime("%b%Y")
        col1, col2 = st.columns(2)
        
        with col1:
            #temporary download button to check transformed data
            st.download_button(
                label="Download Cleaned Excel File",
                data=st.session_state["report_1_data"],
                file_name="Cleaned_Commitments.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            #second download button
        with col2:
            st.download_button(
                label="Download Report 2",
                data=st.session_state["report_2_data"],
                file_name=f"Commitments Overdue and due in the next 6 months-{current_month_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


if __name__ == "__main__":
    main()
