from models import PurchaseOrderLineItem, Invoice, InvoiceLineItem
from numpy import nan
import pandas as pd
from sqlalchemy import exists, func
from sqlalchemy.orm import Session
from typing import NamedTuple, Union


class SummaryAndReconciliationReport(NamedTuple):
    summary: pd.DataFrame
    reconciliation_report: pd.DataFrame


class RawData(NamedTuple):
    purchase_order_lines: pd.DataFrame
    invoice_lines: pd.DataFrame


def classify_variance(x: Union[int, nan]) -> str:
    if pd.isna(x):
        return "Item not in PO"
    elif x < 0:
        return "Under-Invoiced"
    elif x > 0:
        return "Over-Invoiced"
    else:
        return "Fully Matched"


def summary_and_reconciliation(
    session: Session, purchase_order_id: str
) -> SummaryAndReconciliationReport:
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
            grouped_invoice_items_subq.c.invoice_quantity.label("invoice_quantity"),
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
    report_df = pd.DataFrame(report_data, columns=report_columns)
    report_df.insert(
        4, "Qty Variance", report_df["Invoiced Qty"] - report_df["Ordered Qty"]
    )
    report_df.insert(
        7, "Price Variance", report_df["Invoiced Price"] - report_df["Ordered Price"]
    )
    report_df.insert(
        8, "Status / Comments", report_df["Qty Variance"].apply(classify_variance)
    )

    ordered_price_total = report_df["Ordered Price"].sum()
    invoiced_price_total = report_df["Invoiced Price"].sum()
    mismatch_count = (report_df["Ordered Qty"] != report_df["Invoiced Qty"]).sum()
    summary_df = pd.DataFrame(
        {
            "Ordered Price Total": [ordered_price_total],
            "Invoiced Price Total": [invoiced_price_total],
            "Total Variance": [invoiced_price_total - ordered_price_total],
            "Count of Mismatches": [mismatch_count],
        }
    )

    return SummaryAndReconciliationReport(summary_df, report_df)


def items_not_in_purchase_order(
    session: Session, purchase_order_id: str
) -> pd.DataFrame:
    subq = (
        session.query(PurchaseOrderLineItem.id)
        .filter(
            PurchaseOrderLineItem.purchase_order_id == Invoice.purchase_order_id,
            PurchaseOrderLineItem.item_code == InvoiceLineItem.item_code,
        )
        .exists()
    )

    query = (
        session.query(
            InvoiceLineItem.invoice_id,
            InvoiceLineItem.item_code,
            InvoiceLineItem.description,
            InvoiceLineItem.quantity,
            InvoiceLineItem.unit_price,
            InvoiceLineItem.total_price,
        )
        .join(Invoice)
        .filter(Invoice.purchase_order_id == purchase_order_id)
        .filter(~subq)
    )

    return pd.read_sql(query.statement, session.bind)


def purchase_order_lines_without_invoice(
    session: Session,
    purchase_order_id: str,
) -> pd.DataFrame:

    subq = (
        session.query(InvoiceLineItem.id)
        .join(Invoice)
        .filter(
            Invoice.purchase_order_id == purchase_order_id,
            InvoiceLineItem.item_code == PurchaseOrderLineItem.item_code,
        )
        .exists()
    )

    query = (
        session.query(
            PurchaseOrderLineItem.purchase_order_id.label("PO Number"),
            PurchaseOrderLineItem.item_code.label("Item Code"),
            PurchaseOrderLineItem.description.label("Description"),
            PurchaseOrderLineItem.quantity.label("Ordered Qty"),
            PurchaseOrderLineItem.unit_price.label("Unit Price"),
            PurchaseOrderLineItem.total_price.label("Total Price"),
        )
        .filter(PurchaseOrderLineItem.purchase_order_id == purchase_order_id)
        .filter(~subq)
    )

    return pd.read_sql(query.statement, session.bind)


# Edit this to just get the line items.
def raw_data(session: Session, purchase_order_id: str) -> RawData:
    # --- PO Lines ---
    po_query = session.query(
        PurchaseOrderLineItem.purchase_order_id.label("PO Number"),
        PurchaseOrderLineItem.purchase_order_line_number.label("PO Line"),
        PurchaseOrderLineItem.item_code.label("Item Code"),
        PurchaseOrderLineItem.description.label("Description"),
        PurchaseOrderLineItem.quantity.label("Ordered Qty"),
        PurchaseOrderLineItem.unit_price.label("Unit Price"),
        PurchaseOrderLineItem.total_price.label("Total Price"),
    ).filter(PurchaseOrderLineItem.purchase_order_id == purchase_order_id)

    po_lines_df = pd.read_sql(po_query.statement, session.bind)

    # --- Invoice Lines ---
    invoice_query = (
        session.query(
            Invoice.purchase_order_id.label("PO Number"),
            InvoiceLineItem.item_code.label("Item Code"),
            InvoiceLineItem.description.label("Description"),
            InvoiceLineItem.quantity.label("Invoiced Qty"),
            InvoiceLineItem.unit_price.label("Unit Price"),
            InvoiceLineItem.total_price.label("Total Price"),
            Invoice.id.label("Invoice Number"),
        )
        .join(InvoiceLineItem, Invoice.id == InvoiceLineItem.invoice_id)
        .filter(Invoice.purchase_order_id == purchase_order_id)
    )

    invoice_lines_df = pd.read_sql(invoice_query.statement, session.bind)

    # Return as NamedTuple
    return RawData(po_lines_df, invoice_lines_df)
