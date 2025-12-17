# app/test/test_ingest.py
import pytest
from src.models import PurchaseOrder, PurchaseOrderLineItem
from sqlalchemy.exc import IntegrityError


def test_create_purchase_order_with_duplicate_line_number(db_session):
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)

    LINE_NUMBER = 1

    line_item = PurchaseOrderLineItem(
        purchase_order_id=po_id,
        purchase_order_line_number=LINE_NUMBER,
        item_code="ITEM-001",
        description="Test Item",
        quantity=10,
        unit_price=5.0,
        total_price=50.0,
    )
    db_session.add(line_item)
    db_session.flush()

    with pytest.raises(IntegrityError):
        line_item_with_duplicate_line_number = PurchaseOrderLineItem(
            purchase_order_id=po_id,
            purchase_order_line_number=LINE_NUMBER,
            item_code="ITEM-002",
            description="Test Item",
            quantity=10,
            unit_price=5.0,
            total_price=50.0,
        )
        db_session.add(line_item_with_duplicate_line_number)
        db_session.flush()


def test_create_purchase_order_with_duplicate_item_code(db_session):
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)

    ITEM_CODE = "ITEM-001"

    line_item = PurchaseOrderLineItem(
        purchase_order_id=po_id,
        purchase_order_line_number=1,
        item_code=ITEM_CODE,
        description="Test Item",
        quantity=10,
        unit_price=5.0,
        total_price=50.0,
    )
    db_session.add(line_item)
    db_session.flush()

    with pytest.raises(IntegrityError):
        line_item_with_duplicate_item_code = PurchaseOrderLineItem(
            purchase_order_id=po_id,
            purchase_order_line_number=1,
            item_code=ITEM_CODE,
            description="Test Item",
            quantity=10,
            unit_price=5.0,
            total_price=50.0,
        )
        db_session.add(line_item_with_duplicate_item_code)
        db_session.flush()


def test_create_purchase_order_line_item_with_invalid_total_price(db_session):
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)

    with pytest.raises(IntegrityError):
        line_item_with_invalid_price = PurchaseOrderLineItem(
            purchase_order_id=po_id,
            purchase_order_line_number=1,
            item_code="ITEM-001",
            description="Test Item",
            quantity=1,
            unit_price=2.0,
            total_price=3.0,
        )
        db_session.add(line_item_with_invalid_price)
        db_session.flush()


def test_create_purchase_order_with_one_line_item(db_session):
    # Arrange: prepare a PurchaseOrder and one line item
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


def test_create_purchase_order_with_multiple_lines_items(db_session):
    # Arrange: prepare a PurchaseOrder and line items
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)

    num_line_items = 10
    db_session.add_all(
        [
            PurchaseOrderLineItem(
                purchase_order_id=po_id,
                purchase_order_line_number=i + 1,
                item_code=f"ITEM-{str(i).zfill(3)}",
                description=f"Test Item {i}",
                quantity=i,
                unit_price=i,
                total_price=i**2,
            )
            for i in range(num_line_items)
        ]
    )

    # Act: flush to the DB
    db_session.flush()

    # Assert: query the DB to make sure it was inserted
    po_from_db = db_session.get(PurchaseOrder, po_id)
    assert po_from_db is not None
    assert po_from_db.id == po_id

    line_items_from_db = (
        db_session.query(PurchaseOrderLineItem).filter_by(purchase_order_id=po_id).all()
    )
    assert len(line_items_from_db) == num_line_items
    for i in range(num_line_items):
        assert line_items_from_db[i].item_code == f"ITEM-{str(i).zfill(3)}"
