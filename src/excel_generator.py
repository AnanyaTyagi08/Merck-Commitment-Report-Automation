"""Excel report generator for Merck Commitment Reports."""

from pathlib import Path
from typing import Union
import pandas as pd


def build_grt_spmt_workbook(df: pd.DataFrame, output_path: Union[str, Path]) -> None:
    """Generate the formatted Excel workbook with required tabs and views."""
    raise NotImplementedError("Pending implementation")

