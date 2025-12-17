from models import Invoice, InvoiceLineItem, PurchaseOrder
from pandas import DataFrame
from sqlalchemy.orm import Session


def invoice(
    session: Session,
    df: DataFrame,
) -> str:
    purchase_order_id = df["PO Number"].iat[0]
    purchase_order = session.get(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        raise Exception("No purchase order")

    invoice = Invoice(
        id=df["Invoice Number"].iat[0],
        purchase_order_id=purchase_order_id,
    )
    session.add(invoice)

    session.add_all(
        [
            InvoiceLineItem(
                invoice_id=invoice.id,
                item_code=row["Item Code"],
                description=row["Description"],
                quantity=row["Invoiced Qty"],
                unit_price=row["Unit Price"],
                total_price=row["Total Amount"],
            )
            for _, row in df.iterrows()
        ]
    )

    return purchase_order_id
