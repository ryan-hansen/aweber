"""Widget SQLAlchemy model definition."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Widget(Base):
    """Widget model representing a widget entity with parts and timestamps.

    Attributes:
        id: Auto-generated primary key
        name: Widget name (max 64 characters, required, indexed)
        number_of_parts: Number of parts (positive integer, required)
        created_at: Creation timestamp (auto-generated, indexed)
        updated_at: Last update timestamp (auto-updated)
    """

    __tablename__ = "widgets"

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Auto-generated primary key",
    )

    # Widget name - required, max 64 chars, indexed
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Widget name (max 64 characters)",
    )

    # Number of parts - positive integer, required
    number_of_parts: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("number_of_parts > 0", name="positive_parts_check"),
        nullable=False,
        doc="Number of parts (must be positive)",
    )

    # Timestamps - auto-generated and indexed
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last update timestamp",
    )

    def __repr__(self) -> str:
        """Return a string representation of the Widget instance."""
        return (
            f"Widget(id={self.id}, name='{self.name}', "
            f"number_of_parts={self.number_of_parts}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Widget '{self.name}' with {self.number_of_parts} parts"
