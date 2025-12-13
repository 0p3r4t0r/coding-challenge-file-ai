from models import Invoice, InvoiceLineItem, PurchaseOrder, PurchaseOrderLineItem
import validators

from dotenv import load_dotenv
from os import environ
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Dict, List

APP_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = APP_DIR / "files"
INPUT_DIR = FILES_DIR / "input"
OUTPUT_DIR = FILES_DIR / "output"

PURCHASE_ORDER_COLUMNS = [
    "PO Number",
    "PO Line",
    "Item Code",
    "Description",
    "Ordered Qty",
    "Unit Price",
    "Total Amount",
]
INVOICE_COLUMNS = [
    "Invoice Number",
    "PO Number",
    "Item Code",
    "Description",
    "Invoiced Qty",
    "Unit Price",
    "Total Amount",
]


################################################################################
# DB Connection
################################################################################
load_dotenv()
engine = create_engine(
    f"postgresql+psycopg://{environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@{environ.get('POSTGRES_HOST')}:5432/{environ.get('POSTGRES_DB')}"
)


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
    message = f"[[Excel File: {event}]] file: {file.name} sheet: {sheet_name}"
    logger(message)


################################################################################
# Logging
################################################################################
def main():
    # TODO: refactor to require 1 invoice per file.
    for file in INPUT_DIR.iterdir():
        sheets: Dict[str, pd.DataFrame] = pd.read_excel(file, sheet_name=None)
        for sheet_name, df in sheets.items():
            if df.empty:
                log_excel_file_event("Empty Sheet", file, sheet_name)
                continue

            if (
                validators.validate_columns(df, PURCHASE_ORDER_COLUMNS)
                and validators.column_is_constant(df["PO Number"])
                and df["PO Line"].is_unique
                # TODO: Validate that PO Line goes like 1, 2, 3, 4.... in order and no values skipped
                and df["Item Code"].is_unique
                and validators.column_is_integer(df["Ordered Qty"])
                and validators.column_has_at_most_two_decimal_places(df["Unit Price"])
                and validators.column_has_at_most_two_decimal_places(df["Total Amount"])
                and (df["Ordered Qty"] * df["Unit Price"] == df["Total Amount"]).all()
            ):
                log_excel_file_event("Ingesting Purchase Order", file, sheet_name)
                with Session(engine) as session:
                    purchase_order = PurchaseOrder(id=df["PO Number"].iat[0])
                    session.add(purchase_order)

                    for _, row in df.iterrows():
                        line_item = PurchaseOrderLineItem(
                            purchase_order_id=purchase_order.id,
                            purchase_order_line_number=row["PO Line"],
                            item_code=row["Item Code"],
                            description=row["Description"],
                            quantity=row["Ordered Qty"],
                            unit_price=row["Unit Price"],
                            total_price=row["Total Amount"],
                        )
                        session.add(line_item)
                    session.commit()
                log_excel_file_event("Ingested Purchase Order", file, sheet_name)
                ...
            elif (
                validators.validate_columns(df, INVOICE_COLUMNS)
                and validators.column_is_constant(df["Invoice Number"])
                and validators.column_is_constant(df["PO Number"])
                and df["Item Code"].is_unique
                and validators.column_is_integer(df["Invoiced Qty"])
                and validators.column_has_at_most_two_decimal_places(df["Unit Price"])
                and validators.column_has_at_most_two_decimal_places(df["Total Amount"])
                and (df["Invoiced Qty"] * df["Unit Price"] == df["Total Amount"]).all()
            ):
                log_excel_file_event("Ingesting Invoice", file, sheet_name)
                with Session(engine) as session:
                    purchase_order_id = df["PO Number"].iat[0]
                    purchase_order = session.get(PurchaseOrder, purchase_order_id)
                    if not purchase_order:
                        raise Exception("No purchase order")

                    invoice = Invoice(
                        id=df["Invoice Number"].iat[0],
                        purchase_order_id=purchase_order.id,
                    )
                    session.add(invoice)

                    for _, row in df.iterrows():
                        line_item = InvoiceLineItem(
                            invoice_id=invoice.id,
                            item_code=row["Item Code"],
                            description=row["Description"],
                            quantity=row["Invoiced Qty"],
                            unit_price=row["Unit Price"],
                            total_price=row["Total Amount"],
                        )
                        session.add(line_item)
                    session.commit()
                log_excel_file_event("Ingested Invoice", file, sheet_name)
                ...
            else:
                log_excel_file_event("Unsupported Format", file, sheet_name)


if __name__ == "__main__":
    main()
