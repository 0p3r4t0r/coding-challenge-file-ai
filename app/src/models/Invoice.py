from .base import Base
from .PurchaseOrder import PurchaseOrder, PurchaseOrderLineItem

from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Text, primary_key=True)

    purchase_order_id = Column(
        Text, ForeignKey("purchase_order.id", ondelete="CASCADE"), nullable=True
    )

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    line_items = relationship(
        "InvoiceLineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="invoices",
        passive_deletes=True,
    )


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_item"

    id = Column(Integer, primary_key=True)

    invoice_id = Column(
        Text, ForeignKey("invoice.id", ondelete="CASCADE"), nullable=False
    )

    item_code = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        UniqueConstraint("invoice_id", "item_code"),
    )

    invoice = relationship(
        "Invoice",
        back_populates="line_items",
        passive_deletes=True,
    )
