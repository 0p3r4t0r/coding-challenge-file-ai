# app/test/test_ingest.py
import pytest
from src.models import PurchaseOrder, Invoice, InvoiceLineItem
from sqlalchemy.exc import IntegrityError


def test_create_invoice_with_duplicate_item_code(db_session):
    # Create a purchase order first, since invoice references it
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)
    db_session.flush()

    # Create an invoice referencing that purchase order
    invoice_id = "INV-12345"
    invoice = Invoice(id=invoice_id, purchase_order_id=po_id)
    db_session.add(invoice)
    db_session.flush()

    ITEM_CODE = "ITEM-001"

    # Add first line item
    line_item = InvoiceLineItem(
        invoice_id=invoice_id,
        item_code=ITEM_CODE,
        description="Test Item",
        quantity=10,
        unit_price=5.0,
        total_price=50.0,
    )
    db_session.add(line_item)
    db_session.flush()

    # Attempt to add a duplicate line item for the same invoice
    with pytest.raises(IntegrityError):
        duplicate_line_item = InvoiceLineItem(
            invoice_id=invoice_id,
            item_code=ITEM_CODE,  # duplicate item code
            description="Test Item Duplicate",
            quantity=5,
            unit_price=5.0,
            total_price=25.0,
        )
        db_session.add(duplicate_line_item)
        db_session.flush()


def test_create_invoice_line_item_with_invalid_total_price(db_session):
    # Create a purchase order first
    po_id = "PO-12345"
    po = PurchaseOrder(id=po_id)
    db_session.add(po)
    db_session.flush()

    # Create an invoice referencing the purchase order
    invoice_id = "INV-12345"
    invoice = Invoice(id=invoice_id, purchase_order_id=po_id)
    db_session.add(invoice)
    db_session.flush()

    # Attempt to create a line item with incorrect total_price
    with pytest.raises(IntegrityError):
        invalid_line_item = InvoiceLineItem(
            invoice_id=invoice_id,
            item_code="ITEM-001",
            description="Test Item",
            quantity=1,
            unit_price=2.0,
            total_price=3.0,  # Invalid: should be 1 * 2.0 = 2.0
        )
        db_session.add(invalid_line_item)
        db_session.flush()
