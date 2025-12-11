from typing import List
import pandas as pd


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
    po = pd.read_excel('PO.xlsx')
    invoice1 = pd.read_excel('Invoices.xlsx', sheet_name="Invoice1")
    invoice2 = pd.read_excel('Invoices.xlsx', sheet_name="Invoice2")
    invoice3 = pd.read_excel('Invoices.xlsx', sheet_name="Invoice3")
    print(po.head())
    print(invoice1.head())
    print(invoice2.head())
    print(invoice3.head())


if __name__ == "__main__":
    main()
