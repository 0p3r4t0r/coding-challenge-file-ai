import identifiers
import ingestors
import validators

from collections import deque
from datetime import datetime
from dotenv import load_dotenv
import logging
from os import environ
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import sys

import reports

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
# Logging
################################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def log_excel_file_event(event: str, file: Path) -> str:
    message = f"[[Excel Event: {event}]] First sheet of file: {file.name}"
    logging.info(message)


################################################################################
# Queue
################################################################################
report_purchase_order_ids_queue = deque()
report_purchase_order_ids_set = set()


def enqueue_purchase_order_id(id: str) -> bool:
    if id not in report_purchase_order_ids_set:
        report_purchase_order_ids_queue.append(id)
        report_purchase_order_ids_set.add(id)
        return True
    return False


def dequeue_purchase_order_id() -> str:
    id = report_purchase_order_ids_queue.popleft()
    report_purchase_order_ids_set.remove(id)
    return id


################################################################################
# DB Connection
################################################################################
load_dotenv()
engine = create_engine(
    f"postgresql+psycopg://{environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@{environ.get('POSTGRES_HOST')}:5432/{environ.get('POSTGRES_DB')}"
)


################################################################################
# Main
################################################################################
sorted_filenames = sorted(
    INPUT_DIR.iterdir(), key=lambda x: 0 if x.name.startswith("PurchaseOrder") else 1
)


def main():
    for file in sorted_filenames:
        df = pd.read_excel(file, sheet_name=0)
        if df.empty:
            log_excel_file_event("No data", file)
            continue

        if not validators.validate_file_name(file):
            logging.info(
                f'File name does not start with "PurchaseOrder" or "Invoice": {file.name}'
            )
            continue

        if (
            identifiers.by_columns(df, PURCHASE_ORDER_COLUMNS)
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
                    purchase_order_id = ingestors.purchase_order(session, df)
                    ingestors.file(OUTPUT_DIR, file)
                    session.commit()
                    enqueue_purchase_order_id(purchase_order_id)
                    log_excel_file_event("Ingested Purchase Order", file)
            except Exception as e:
                log_excel_file_event("Failed to Ingest Purchase Order", file)
                logging.error(e)
        elif (
            identifiers.by_columns(df, INVOICE_COLUMNS)
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
                    purchase_order_id = ingestors.invoice(session, df)
                    ingestors.file(OUTPUT_DIR, file)
                    session.commit()
                    enqueue_purchase_order_id(purchase_order_id)
                    log_excel_file_event("Ingested Invoice", file)
            except Exception as e:
                log_excel_file_event("Failed to Ingest Invoice", file)
                logging.error(e)
        else:
            log_excel_file_event("Unsupported Format", file)

    while report_purchase_order_ids_queue:
        purchase_order_id = dequeue_purchase_order_id()

        with Session(engine) as session:
            session.connection(
                execution_options={"isolation_level": "REPEATABLE READ"},
            )

            now = datetime.now()
            current_timestamp = now.strftime("%Y%m%d_%H%M%S")
            filename = f"report_{purchase_order_id}_{current_timestamp}.xlsx"

            summary, reconciliation_report = reports.summary_and_reconciliation(
                session, purchase_order_id
            )
            items_not_in_purchase_order = reports.items_not_in_purchase_order(
                session, purchase_order_id
            )
            purchase_order_lines_without_invoice = (
                reports.purchase_order_lines_without_invoice(session, purchase_order_id)
            )
            purchase_order_lines, invoice_lines = reports.raw_data(
                session, purchase_order_id
            )

            with pd.ExcelWriter(
                OUTPUT_DIR / "reports" / filename, engine="xlsxwriter"
            ) as writer:
                summary.to_excel(writer, sheet_name="Summary", index=False, na_rep="--")
                reconciliation_report.to_excel(
                    writer, sheet_name="Reconciliation Report", index=False, na_rep="--"
                )
                items_not_in_purchase_order.to_excel(
                    writer, sheet_name="Items Not In PO", index=False, na_rep="--"
                )
                purchase_order_lines_without_invoice.to_excel(
                    writer,
                    sheet_name="PO Lines Without Invoice",
                    index=False,
                    na_rep="--",
                )
                purchase_order_lines.to_excel(
                    writer, sheet_name="Raw Data -- PO Lines", index=False, na_rep="--"
                )
                invoice_lines.to_excel(
                    writer,
                    sheet_name="Raw Data -- Invoice Lines",
                    index=False,
                    na_rep="--",
                )

                for _, worksheet in writer.sheets.items():
                    worksheet.set_column(0, worksheet.dim_colmax, 20)

            reports.create_report_db_records(session, purchase_order_id)

            session.commit()


if __name__ == "__main__":
    main()
