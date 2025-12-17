from models import PurchaseOrder, PurchaseOrderLineItem
from pandas import DataFrame
from sqlalchemy.orm import Session


def purchase_order(
    session: Session,
    df: DataFrame,
) -> str:
    purchase_order = PurchaseOrder(id=df["PO Number"].iat[0])
    session.add(purchase_order)

    session.add_all(
        [
            PurchaseOrderLineItem(
                purchase_order_id=purchase_order.id,
                purchase_order_line_number=row["PO Line"],
                item_code=row["Item Code"],
                description=row["Description"],
                quantity=row["Ordered Qty"],
                unit_price=row["Unit Price"],
                total_price=row["Total Amount"],
            )
            for _, row in df.iterrows()
        ]
    )

    return purchase_order.id
