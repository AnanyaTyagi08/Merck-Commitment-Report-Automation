"""Streamlit user interface and entry point for Merck Commitment Report Automation."""

import io
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import streamlit as st

from src.excel_generator import (
    apply_sheet_layout,
    build_keytruda_workbook,
    highlight_overdue_rows,
)
from src.report_filenames import get_report_filenames
from src.transforms import (
    filter_grt_spmt_report,
    filter_keytruda_report,
    filter_overdue_and_six_months,
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

    #clearing memory if a new file is uploaded
    if uploaded_file is not None:
        upload_data = uploaded_file.getvalue()
        if upload_data != st.session_state.get("last_uploaded_file"):
            st.session_state.pop("reports", None)
            st.session_state.pop("reports_zip", None)
            st.session_state["last_uploaded_file"] = upload_data

    if st.button("Generate Report", type="primary", disabled=uploaded_file is None):
        st.session_state.pop("reports", None)
        st.session_state.pop("reports_zip", None)
        try:
            with st.spinner("Processing spreadsheet..."):
                report_date = pd.Timestamp.today()
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

                # Use the original export so Keytruda keeps its own date rules.
                keytruda_df = filter_keytruda_report(raw_df, report_date)
                with TemporaryDirectory() as output_dir:
                    keytruda_path = build_keytruda_workbook(
                        keytruda_df, output_dir, report_date
                    )
                    keytruda_data = keytruda_path.read_bytes()

                filenames = get_report_filenames(report_date.date())
                reports = {
                    filenames["grt_spmt"]: buffer.getvalue(),
                    filenames["overdue_and_six_months"]: buffer_2.getvalue(),
                    filenames["keytruda_ongoing"]: keytruda_data,
                }
                zip_buffer = io.BytesIO()
                with ZipFile(zip_buffer, "w", compression=ZIP_DEFLATED) as archive:
                    for filename, data in reports.items():
                        archive.writestr(filename, data)

                # Keep downloads available across reruns without processing again.
                st.session_state["reports"] = reports
                st.session_state["reports_zip"] = zip_buffer.getvalue()

        except Exception as e:
            st.error(f"Error processing file: {e}")

    if uploaded_file is not None and "reports" in st.session_state:
        st.success("File processed successfully!")
        for filename, data in st.session_state["reports"].items():
            st.download_button(
                label=f"Download {filename}",
                data=data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.download_button(
            label="Download All Reports (.zip)",
            data=st.session_state["reports_zip"],
            file_name="Commitment Reports.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
