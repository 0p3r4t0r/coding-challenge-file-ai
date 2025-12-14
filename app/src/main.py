from models import Invoice, InvoiceLineItem, PurchaseOrder, PurchaseOrderLineItem
import validators

from collections import deque
from decimal import Decimal
from dotenv import load_dotenv
from os import environ
from numpy import nan
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from typing import Union


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


def log_excel_file_event(event: str, file: Path) -> str:
    message = f"[[Excel Event: {event}]] First sheet of file: {file.name}"
    logger(message)


################################################################################
# Utils
################################################################################
def classify_variance(x: Union[int, nan]) -> str:
    if pd.isna(x):
        return "Item not in PO"
    elif x < 0:
        return "Under-Invoiced"
    elif x > 0:
        return "Over-Invoiced"
    else:
        return "Fully Matched"


################################################################################
# Main
################################################################################
sorted_filenames = sorted(
    INPUT_DIR.iterdir(), key=lambda x: 0 if x.name.startswith("PurchaseOrder") else 1
)


def main():
    q = deque()
    s = set()

    q.append("PO-1001")
    s.add("PO-1001")

    while q:
        purchase_order_id = q.popleft()
        s.remove(purchase_order_id)

        with Session(engine) as session:
            grouped_invoice_items_subq = (
                session.query(
                    InvoiceLineItem.item_code.label("invoice_item_code"),
                    func.sum(InvoiceLineItem.quantity).label("invoice_quantity"),
                    func.sum(InvoiceLineItem.total_price).label("invoice_total_price"),
                )
                .join(Invoice)
                .filter(Invoice.purchase_order_id == purchase_order_id)
                .group_by(InvoiceLineItem.item_code, InvoiceLineItem.description)
                .subquery()
            )

            report_data = (
                session.query(
                    func.coalesce(
                        PurchaseOrderLineItem.purchase_order_id, purchase_order_id
                    ).label("purchase_order_id"),
                    func.coalesce(
                        PurchaseOrderLineItem.item_code,
                        grouped_invoice_items_subq.c.invoice_item_code,
                    ).label("item_code"),
                    PurchaseOrderLineItem.quantity.label("po_quantity"),
                    grouped_invoice_items_subq.c.invoice_quantity.label(
                        "invoice_quantity"
                    ),
                    PurchaseOrderLineItem.total_price.label("po_total_price"),
                    grouped_invoice_items_subq.c.invoice_total_price.label(
                        "invoice_total_price"
                    ),
                )
                .join(
                    grouped_invoice_items_subq,
                    PurchaseOrderLineItem.item_code
                    == grouped_invoice_items_subq.c.invoice_item_code,
                    full=True,
                )
                .all()
            )

            report_columns = [
                "PO Number",
                "Item Code",
                "Ordered Qty",
                "Invoiced Qty",
                "Ordered Price",
                "Invoiced Price",
            ]
            df = pd.DataFrame(report_data, columns=report_columns)
            df.insert(4, "Qty Variance", df["Invoiced Qty"] - df["Ordered Qty"])
            df.insert(7, "Price Variance", df["Invoiced Price"] - df["Ordered Price"])
            df.insert(
                8, "Status / Comments", df["Qty Variance"].apply(classify_variance)
            )

            print(df)
            ordered_price_total = df["Ordered Price"].sum()
            invoiced_price_total = df["Invoiced Price"].sum()
            total_variance = invoiced_price_total - ordered_price_total
            mismatch_count = (df["Ordered Qty"] != df["Invoiced Qty"]).sum()
            print(
                f"Ordered Price: {ordered_price_total}, Invoiced Price: {invoiced_price_total}, Total Variance: {total_variance}, Mismatch Count: {mismatch_count}"
            )

    return
    for file in sorted_filenames:
        df = pd.read_excel(file, sheet_name=0)
        if df.empty:
            log_excel_file_event("No data", file)
            continue

        if not validators.validate_file_name(file):
            logger(
                f'File name does not start with "PurchaseOrder" or "Invoice": {file.name}'
            )

        if (
            validators.validate_columns(df, PURCHASE_ORDER_COLUMNS)
            and validators.column_is_constant(df["PO Number"])
            and validators.column_po_line(df["PO Line"])
            and df["Item Code"].is_unique
            and validators.column_is_integer(df["Ordered Qty"])
            and validators.column_has_at_most_two_decimal_places(df["Unit Price"])
            and validators.column_has_at_most_two_decimal_places(df["Total Amount"])
            and (df["Ordered Qty"] * df["Unit Price"] == df["Total Amount"]).all()
        ):
            log_excel_file_event("Ingesting Purchase Order", file)
            try:
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
            except Exception as e:
                log_excel_file_event("Failed to Ingest Purchase Order", file)
                logger(e)

            log_excel_file_event("Ingested Purchase Order", file)
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
            log_excel_file_event("Ingesting Invoice", file)
            try:
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
            except Exception as e:
                log_excel_file_event("Failed to Ingest Invoice", file)
                logger(e)

            log_excel_file_event("Ingested Invoice", file)
            ...
        else:
            log_excel_file_event("Unsupported Format", file)


if __name__ == "__main__":
    main()
