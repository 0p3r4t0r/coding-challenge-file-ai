# app/test/test_ingest.py
import pytest
from src.models import PurchaseOrder, PurchaseOrderLineItem


def test_create_purchase_order(db_session):
    # Arrange: prepare a PurchaseOrder and line items
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)

    line_item = PurchaseOrderLineItem(
        purchase_order_id=po_id,
        purchase_order_line_number=1,
        item_code="ITEM-001",
        description="Test Item",
        quantity=10,
        unit_price=5.0,
        total_price=50.0,
    )
    db_session.add(line_item)

    # Act: flush to the DB
    db_session.flush()

    # Assert: query the DB to make sure it was inserted
    po_from_db = db_session.get(PurchaseOrder, po_id)
    assert po_from_db is not None
    assert po_from_db.id == po_id

    line_items_from_db = (
        db_session.query(PurchaseOrderLineItem).filter_by(purchase_order_id=po_id).all()
    )
    assert len(line_items_from_db) == 1
    assert line_items_from_db[0].item_code == "ITEM-001"
