"""Verify processing and downloadable report contents through the UI entry point."""

import io
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import pandas as pd
from openpyxl import load_workbook

from src.app import main
from src.report_filenames import get_report_filenames


def make_upload(product="pembrolizumab"):
    upload = io.BytesIO()
    df = pd.DataFrame({
        "Primary Product Family": [product],
        "Commitment Lifecycle State": ["Ongoing"],
        "Completed State Qualifier": [""],
        "Country Name": ["Canada"],
        "Working Due Date": [pd.Timestamp.today().normalize() - pd.Timedelta(days=1)],
        "Commitment Due Date": [pd.NaT],
    })
    with pd.ExcelWriter(upload, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Export", startrow=1, index=False)
    upload.seek(0)
    upload.name = "input.xlsx"
    upload.size = len(upload.getvalue())
    return upload


def test_process_and_downloads_survive_reruns():
    ui = MagicMock()
    ui.session_state = {}
    ui.file_uploader.return_value = make_upload()
    ui.button.return_value = True
    with patch("src.app.st", ui):
        main()
        assert not ui.error.called
        downloads = [call.kwargs for call in ui.download_button.call_args_list]
        filenames = get_report_filenames()
        assert [item["file_name"] for item in downloads[:3]] == [
            filenames["grt_spmt"],
            filenames["overdue_and_six_months"],
            filenames["keytruda_ongoing"],
        ]
        for item in downloads[:3]:
            workbook = load_workbook(io.BytesIO(item["data"]))
            assert workbook.active.max_row >= 2
            assert workbook.active.freeze_panes is not None
            workbook.close()
        assert downloads[3]["label"] == "Download All Reports (.zip)"
        with ZipFile(io.BytesIO(downloads[3]["data"])) as archive:
            assert archive.namelist() == [item["file_name"] for item in downloads[:3]]
            for item in downloads[:3]:
                assert archive.read(item["file_name"]) == item["data"]

        ui.button.return_value = False
        ui.download_button.reset_mock()
        with patch("src.app.pd.read_excel") as read_excel:
            main()
            read_excel.assert_not_called()
        assert ui.download_button.call_count == 4

        # Replacing an upload with the same filename must invalidate old reports.
        ui.file_uploader.return_value = make_upload("other")
        ui.download_button.reset_mock()
        main()
        ui.download_button.assert_not_called()


def test_failed_processing_does_not_offer_stale_downloads():
    ui = MagicMock()
    upload = make_upload()
    ui.session_state = {
        "last_uploaded_file": upload.getvalue(),
        "reports": {"old.xlsx": b"old"},
        "reports_zip": b"old",
    }
    ui.file_uploader.return_value = upload
    ui.button.return_value = True
    with patch("src.app.st", ui), patch(
        "src.app.pd.read_excel", side_effect=ValueError("Invalid spreadsheet")
    ):
        main()
    ui.error.assert_called_once()
    ui.download_button.assert_not_called()
