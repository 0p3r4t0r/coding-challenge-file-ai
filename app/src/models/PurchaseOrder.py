from .base import Base
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


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(Text, primary_key=True)
    created_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )

    line_items = relationship(
        "PurchaseOrderLineItem",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    invoices = relationship(
        "Invoice",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reports = relationship(
        "Report",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PurchaseOrderLineItem(Base):
    __tablename__ = "purchase_order_line_item"

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(
        Text, ForeignKey("purchase_order.id", ondelete="CASCADE"), nullable=False
    )

    purchase_order_line_number = Column(Integer, nullable=False)
    item_code = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("purchase_order_id", "purchase_order_line_number"),
        UniqueConstraint("purchase_order_id", "item_code"),
    )

    purchase_order = relationship(
        "PurchaseOrder", back_populates="line_items", passive_deletes=True
    )
