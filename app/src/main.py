from models import PurchaseOrder, PurchaseOrderLineItem
import validators

from collections import namedtuple
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Dict, List

APP_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = APP_DIR / 'files'
INPUT_DIR = FILES_DIR / 'input'
OUTPUT_DIR = FILES_DIR / 'output'

PURCHASE_ORDER_COLUMNS = ['PO Number', 'PO Line', 'Item Code', 'Description', 'Ordered Qty', 'Unit Price', 'Total Amount']
INVOICE_COLUMNS = ['Invoice Number', 'PO Number', 'Item Code', 'Description', 'Invoiced Qty', 'Unit Price', 'Total Amount']


################################################################################
# DB Connection
################################################################################
# TODO: use .env to set this url.
engine = create_engine('postgresql+psycopg://postgres:password@localhost:5432/database')
with Session(engine) as session:
    purchase_orders = session.query(PurchaseOrder).all()
    print(purchase_orders)


################################################################################
# Logging
################################################################################
def logger(message: str):
    """
    Placeholder function for logging.
    
    During local development, you'll want to print to console.
    On a server you may want to log to a file, or an external system.

    This can be easily accomplished simply by changing the contents of this
    function.
    """
    print(message)


def log_excel_file_event(event: str, file: Path, sheet_name: str) -> str:
    message = f'[[Excel File: {event}]] file: {file.name} sheet: {sheet_name}'
    logger(message)


################################################################################
# Ingestion
################################################################################
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
        sheets: Dict[str, pd.DataFrame] = pd.read_excel(file, sheet_name=None)
        for sheet_name, df in sheets.items():
            if df.empty:
                log_excel_file_event('Empty Sheet', file, sheet_name)
                continue

            if (
                validators.validate_columns(df, PURCHASE_ORDER_COLUMNS)
                and validators.column_is_constant(df['PO Number'])
                and df['PO Line'].is_unique
                and df['Item Code'].is_unique
                and validators.column_is_integer(df['Ordered Qty'])
                and validators.column_has_at_most_two_decimal_places(df['Unit Price'])
                and validators.column_has_at_most_two_decimal_places(df['Total Amount'])
                and (df['Ordered Qty'] * df['Unit Price'] == df['Total Amount']).all()
            ):
                log_excel_file_event('Processing Purchase Order', file, sheet_name)
                ...
            elif (
                validators.validate_columns(df, INVOICE_COLUMNS)
                and validators.column_is_constant(df['Invoice Number'])
                and validators.column_is_constant(df['PO Number'])
                and df['Item Code'].is_unique
                and validators.column_is_integer(df['Invoiced Qty'])
                and validators.column_has_at_most_two_decimal_places(df['Unit Price'])
                and validators.column_has_at_most_two_decimal_places(df['Total Amount'])
                and (df['Invoiced Qty'] * df['Unit Price'] == df['Total Amount']).all()
            ):
                log_excel_file_event('Processing Invoice', file, sheet_name)
                ...
            else:
                log_excel_file_event('Unsupported Format', file, sheet_name)


if __name__ == "__main__":
    main()
