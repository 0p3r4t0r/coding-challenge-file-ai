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
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Text, primary_key=True)

    purchase_order_id = Column(
        Text,
        ForeignKey("purchase_order.id", ondelete="CASCADE"),
        nullable=True,  # your schema allows nulls
    )

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    line_items = relationship(
        "InvoiceLineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Optional: Relationship to PurchaseOrder object
    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="invoices",
        passive_deletes=True,
    )


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_item"

    id = Column(Integer, primary_key=True)

    invoice_id = Column(
        Text,
        ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=True,
    )

    purchase_order_line_item_id = Column(
        Integer,
        ForeignKey("purchase_order_line_item.id", ondelete="CASCADE"),
        nullable=True,
    )

    item_code = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        UniqueConstraint("invoice_id", "item_code"),
    )
