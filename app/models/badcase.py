from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BadcaseTag(Base, TimestampMixin):
    __tablename__ = "badcase_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)

    evaluation_links: Mapped[list["EvaluationResultBadcaseTag"]] = relationship(
        "EvaluationResultBadcaseTag",
        back_populates="badcase_tag",
        cascade="all, delete-orphan",
    )


class EvaluationResultBadcaseTag(Base, TimestampMixin):
    __tablename__ = "evaluation_result_badcase_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluation_result_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_results.id"),
        nullable=False,
        index=True,
    )
    badcase_tag_id: Mapped[int] = mapped_column(ForeignKey("badcase_tags.id"), nullable=False, index=True)

    evaluation_result: Mapped["EvaluationResult"] = relationship("EvaluationResult", back_populates="tag_links")
    badcase_tag: Mapped["BadcaseTag"] = relationship("BadcaseTag", back_populates="evaluation_links")
