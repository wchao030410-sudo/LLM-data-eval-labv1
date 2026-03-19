import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Dataset, Sample
from app.schemas.dataset import DatasetCreate, DatasetUpdate, SampleCreate, SampleUpdate
from app.utils.internal_data import HIDDEN_DATASET_STATUS


class DatasetService:
    def __init__(self, session: Session):
        self.session = session

    def create_dataset(self, payload: DatasetCreate) -> Dataset:
        dataset = Dataset(**payload.model_dump())
        self.session.add(dataset)
        self.session.flush()
        return dataset

    def list_datasets(self, include_hidden: bool = False) -> List[Dataset]:
        stmt = select(Dataset).order_by(Dataset.created_at.desc())
        if not include_hidden:
            stmt = stmt.where(Dataset.status != HIDDEN_DATASET_STATUS)
        return list(self.session.scalars(stmt))

    def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        return self.session.get(Dataset, dataset_id)

    def update_dataset(self, dataset_id: int, payload: DatasetUpdate) -> Dataset:
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError("Dataset not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(dataset, key, value)
        self.session.flush()
        return dataset

    def delete_dataset(self, dataset_id: int) -> None:
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError("Dataset not found")
        self.session.delete(dataset)
        self.session.flush()

    def list_samples(
        self,
        dataset_id: int,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[Sample]:
        stmt = select(Sample).where(Sample.dataset_id == dataset_id).order_by(Sample.id)
        if search:
            pattern = "%{value}%".format(value=search)
            stmt = stmt.where(
                or_(
                    Sample.query.ilike(pattern),
                    Sample.context.ilike(pattern),
                    Sample.reference_answer.ilike(pattern),
                )
            )
        if category:
            stmt = stmt.where(Sample.category == category)
        if difficulty:
            stmt = stmt.where(Sample.difficulty == difficulty)
        return list(self.session.scalars(stmt))

    def get_sample(self, sample_id: int) -> Optional[Sample]:
        return self.session.get(Sample, sample_id)

    def create_sample(self, dataset_id: int, payload: SampleCreate) -> Sample:
        sample = Sample(dataset_id=dataset_id, **payload.model_dump())
        self.session.add(sample)
        self.session.flush()
        self._refresh_sample_count(dataset_id)
        return sample

    def bulk_create_samples(self, dataset_id: int, payloads: List[SampleCreate]) -> List[Sample]:
        created = []
        for payload in payloads:
            created.append(Sample(dataset_id=dataset_id, **payload.model_dump()))
        self.session.add_all(created)
        self.session.flush()
        self._refresh_sample_count(dataset_id)
        return created

    def update_sample(self, sample_id: int, payload: SampleUpdate) -> Sample:
        sample = self.get_sample(sample_id)
        if not sample:
            raise ValueError("Sample not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(sample, key, value)
        self.session.flush()
        return sample

    def import_samples_from_file(self, dataset_id: int, file_path: str) -> int:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        if path.suffix.lower() == ".csv":
            dataframe = pd.read_csv(path)
        elif path.suffix.lower() == ".json":
            dataframe = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
        else:
            raise ValueError("Only CSV and JSON are supported")

        payloads = []
        for record in dataframe.to_dict(orient="records"):
            tags = record.get("tags", [])
            if isinstance(tags, str):
                tags = [item.strip() for item in tags.split("|") if item.strip()]
            payloads.append(
                SampleCreate(
                    query=record["query"],
                    context=record["context"],
                    reference_answer=record["reference_answer"],
                    category=record.get("category", "general"),
                    difficulty=record.get("difficulty", "medium"),
                    tags=tags,
                    notes=record.get("notes", ""),
                )
            )
        self.bulk_create_samples(dataset_id, payloads)
        return len(payloads)

    def _refresh_sample_count(self, dataset_id: int) -> None:
        dataset = self.get_dataset(dataset_id)
        if dataset:
            dataset.sample_count = len(dataset.samples)
            self.session.flush()
