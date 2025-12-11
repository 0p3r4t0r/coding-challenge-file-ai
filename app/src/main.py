import pandas as pd
from pathlib import Path
from typing import List

APP_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = APP_DIR / 'files'
INPUT_DIR = FILES_DIR / 'input'
OUTPUT_DIR = FILES_DIR / 'output'

################################################################################
# Ingestion
################################################################################
def validate_and_normalize_po(po: pd.DataFrame) -> pd.DataFrame:
    ...


def validate_and_normalize_invoice(invoice: pd.DataFrame) -> pd.DataFrame:
    ...



################################################################################
# Analysis
################################################################################

"""
Should take in any number of invoices and aggregate them.
"""
def aggregate_invoices(*invoices: pd.DataFrame) -> pd.DataFrame:
    ...


# Use a named tuple for output
def analyze(po: pd.DataFrame, invoice: pd.DataFrame) -> List[pd.DataFrame]:
    ...


def main():
    po = pd.read_excel(INPUT_DIR / 'PO.xlsx')
    invoice1 = pd.read_excel(INPUT_DIR / 'Invoices.xlsx', sheet_name="Invoice1")
    invoice2 = pd.read_excel(INPUT_DIR / 'Invoices.xlsx', sheet_name="Invoice2")
    invoice3 = pd.read_excel(INPUT_DIR / 'Invoices.xlsx', sheet_name="Invoice3")
    print(po.head())
    print(invoice1.head())
    print(invoice2.head())
    print(invoice3.head())


if __name__ == "__main__":
    main()
