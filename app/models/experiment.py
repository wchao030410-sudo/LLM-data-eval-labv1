from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"), nullable=False, index=True)
    target_model: Mapped[str] = mapped_column(String(120), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    top_p: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, default=512, nullable=False)
    judge_mode: Mapped[str] = mapped_column(String(40), default="rule", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False, index=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="experiments")
    prompt_version: Mapped["PromptVersion"] = relationship("PromptVersion", back_populates="experiments")
    runs: Mapped[list["ExperimentRun"]] = relationship(
        "ExperimentRun",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )


class ExperimentRun(Base, TimestampMixin):
    __tablename__ = "experiment_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"), nullable=False, index=True)
    run_name: Mapped[str] = mapped_column(String(160), nullable=False)
    run_status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sample_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sample_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_correctness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_groundedness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_hallucination_risk: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="runs")
    evaluation_results: Mapped[list["EvaluationResult"]] = relationship(
        "EvaluationResult",
        back_populates="experiment_run",
        cascade="all, delete-orphan",
    )
