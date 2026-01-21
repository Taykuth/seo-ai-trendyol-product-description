from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .db import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("merchant_sku", name="uq_merchant_sku"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    merchant_sku: Mapped[str] = mapped_column(String(128), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(128), nullable=True)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(256), nullable=True)
    category_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    old_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_urls_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generations: Mapped[list["Generation"]] = relationship(back_populates="product")

class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    version: Mapped[int] = mapped_column(Integer, default=1)
    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    generated_html: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # PASS/FAIL
    validation_report_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="generations")
