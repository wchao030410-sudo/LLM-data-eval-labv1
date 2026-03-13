from __future__ import annotations

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    task_type: Mapped[str] = mapped_column(String(60), default="search_qa", nullable=False)
    owner: Mapped[str] = mapped_column(String(80), default="portfolio", nullable=False)

    versions: Mapped[list["PromptVersion"]] = relationship(
        "PromptVersion",
        back_populates="prompt",
        cascade="all, delete-orphan",
    )


class PromptVersion(Base, TimestampMixin):
    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("prompt_id", "version", name="uq_prompt_versions_prompt_id_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    system_prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    few_shot_examples: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    variables_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    change_note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="versions")
    experiments: Mapped[list["Experiment"]] = relationship("Experiment", back_populates="prompt_version")
