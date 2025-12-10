import pandas as pd


################################################################################
# Data Ingestion
################################################################################

def validate_po_data():
    ...


def validate_invoice_data():
    ...


def aggregate_invoices():
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
