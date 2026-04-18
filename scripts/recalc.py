"""Recalculate all formulas in an Excel workbook and save.

Uses win32com (Excel COM automation) on Windows to force a full
recalculation so every formula cell gets a cached value.

Usage:
    python scripts/recalc.py <path_to_xlsx>

Example:
    python scripts/recalc.py QuotationSheet/Delhi_PS_CRM_Quotation.xlsx
"""

from __future__ import annotations

import sys
from pathlib import Path


def recalc(xlsx_path: str) -> None:
    resolved = Path(xlsx_path).resolve()
    if not resolved.exists():
        print(f"ERROR: File not found: {resolved}")
        sys.exit(1)

    try:
        import win32com.client  # type: ignore[import-untyped]
    except ImportError:
        print(
            "WARNING: pywin32 is not installed.  Install it with:\n"
            "    pip install pywin32\n"
            "Formulas will be evaluated when the file is opened in Excel."
        )
        return

    print(f"Opening {resolved} in Excel for recalculation ...")
    xl = win32com.client.Dispatch("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False

    try:
        wb = xl.Workbooks.Open(str(resolved))
        xl.CalculateFullRebuild()
        wb.Save()
        wb.Close(False)
        print("Recalculation complete — cached values updated.")
    except Exception as exc:
        print(f"ERROR during recalc: {exc}")
        sys.exit(1)
    finally:
        xl.Quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/recalc.py <path_to_xlsx>")
        sys.exit(1)
    recalc(sys.argv[1])
