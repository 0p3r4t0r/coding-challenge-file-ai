from .base import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(
        Text,
        ForeignKey("purchase_order.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="reports",
        passive_deletes=True,
    )

    invoices = relationship(
        "Invoice",
        secondary="report_invoice",
        back_populates="reports",
        passive_deletes=True,
    )


class ReportInvoice(Base):
    __tablename__ = "report_invoice"

    id = Column(Integer, primary_key=True)

    report_id = Column(
        Integer,
        ForeignKey("report.id", ondelete="CASCADE"),
        nullable=False,
    )

    invoice_id = Column(
        Text,
        ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (UniqueConstraint("report_id", "invoice_id"),)
