from models import PurchaseOrder, PurchaseOrderLineItem

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import List

APP_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = APP_DIR / 'files'
INPUT_DIR = FILES_DIR / 'input'
OUTPUT_DIR = FILES_DIR / 'output'


# TODO: use .env to set this url.
engine = create_engine('postgresql+psycopg://postgres:password@localhost:5432/database')
with Session(engine) as session:
    purchase_orders = session.query(PurchaseOrder).all()
    print(purchase_orders)

################################################################################
# Ingestion
################################################################################
def is_purchase_order(df: pd.DataFrame) -> bool:
    expected = ['PO Number', 'PO Line', 'Item Code', 'Description', 'Ordered Qty', 'Unit Price', 'Total Amount']
    actual = df.columns.to_list()

    if len(actual) != len(expected):
        return False

    for i in range(len(expected)):
        if expected[i] != actual[i]:
            return False
    
    return True


def is_invoice(df: pd.DataFrame) -> bool:
    expected = ['Invoice Number', 'PO Number', 'Item Code', 'Description', 'Invoiced Qty', 'Unit Price', 'Total Amount']
    actual = df.columns.to_list()

    if len(actual) != len(expected):
        return False

    for i in range(len(expected)):
        if expected[i] != actual[i]:
            return False
    
    return True


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
    for file in INPUT_DIR.iterdir():
        sheets = pd.read_excel(file, sheet_name=None)
        for sheet_name, df in sheets.items():
            if not df.empty:
                if is_purchase_order(df):
                    print(f'[Processing purchase order: sheet {sheet_name} file {file.name}]')
                    print(df.head(1)["PO Number"])
                elif is_invoice(df):
                    print(f'[Processing invoice order: sheet {sheet_name} file {file.name}]')
                    print(df.head(1))
                    ...
                else:
                    print(f'[Unrecognized file type sheet {sheet_name} file {file.name}]')


if __name__ == "__main__":
    main()
