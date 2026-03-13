from __future__ import annotations

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EvaluationResult(Base, TimestampMixin):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_run_id: Mapped[int] = mapped_column(ForeignKey("experiment_runs.id"), nullable=False, index=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"), nullable=False, index=True)
    generated_answer: Mapped[str] = mapped_column(Text, nullable=False)
    rendered_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    correctness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completeness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    groundedness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    format_compliance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hallucination_risk: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    judge_detail: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_bad_case: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    experiment_run: Mapped["ExperimentRun"] = relationship("ExperimentRun", back_populates="evaluation_results")
    sample: Mapped["Sample"] = relationship("Sample", back_populates="evaluation_results")
    tag_links: Mapped[list["EvaluationResultBadcaseTag"]] = relationship(
        "EvaluationResultBadcaseTag",
        back_populates="evaluation_result",
        cascade="all, delete-orphan",
    )
