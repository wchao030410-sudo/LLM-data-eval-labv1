from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Prompt, PromptVersion
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptVersionCreate, PromptVersionUpdate
from app.utils.prompting import build_prompt_messages, stringify_messages


class PromptService:
    def __init__(self, session: Session):
        self.session = session

    def create_prompt(self, payload: PromptCreate) -> Prompt:
        prompt = Prompt(**payload.model_dump())
        self.session.add(prompt)
        self.session.flush()
        return prompt

    def list_prompts(self) -> List[Prompt]:
        stmt = select(Prompt).options(selectinload(Prompt.versions)).order_by(Prompt.created_at.desc())
        return list(self.session.scalars(stmt))

    def get_prompt(self, prompt_id: int) -> Optional[Prompt]:
        stmt = select(Prompt).options(selectinload(Prompt.versions)).where(Prompt.id == prompt_id)
        return self.session.scalars(stmt).first()

    def update_prompt(self, prompt_id: int, payload: PromptUpdate) -> Prompt:
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError("Prompt not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(prompt, key, value)
        self.session.flush()
        return prompt

    def create_prompt_version(self, payload: PromptVersionCreate) -> PromptVersion:
        version = PromptVersion(**payload.model_dump())
        self.session.add(version)
        self.session.flush()
        return version

    def list_versions(self, prompt_id: Optional[int] = None) -> List[PromptVersion]:
        stmt = select(PromptVersion).order_by(PromptVersion.created_at.desc())
        if prompt_id:
            stmt = stmt.where(PromptVersion.prompt_id == prompt_id)
        return list(self.session.scalars(stmt))

    def get_prompt_version(self, version_id: int) -> Optional[PromptVersion]:
        return self.session.get(PromptVersion, version_id)

    def update_prompt_version(self, version_id: int, payload: PromptVersionUpdate) -> PromptVersion:
        version = self.get_prompt_version(version_id)
        if not version:
            raise ValueError("Prompt version not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(version, key, value)
        self.session.flush()
        return version

    def render_prompt(self, prompt_version: PromptVersion, sample) -> Tuple[list, str]:
        messages = build_prompt_messages(prompt_version, sample)
        return messages, stringify_messages(messages)
