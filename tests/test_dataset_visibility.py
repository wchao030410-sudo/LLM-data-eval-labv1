import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.base import Base
from app.schemas.dataset import DatasetCreate
from app.services.dataset_service import DatasetService
from app.utils.internal_data import HIDDEN_DATASET_STATUS


def test_list_datasets_hides_internal_shadow_datasets_by_default():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, future=True, class_=Session)

    with SessionLocal() as session:
        service = DatasetService(session)
        service.create_dataset(
            DatasetCreate(
                name="公开演示集",
                description="public",
                source_type="demo",
                source_path="generated://public",
                status="active",
            )
        )
        service.create_dataset(
            DatasetCreate(
                name="金融影子评测集",
                description="shadow",
                source_type="internal_demo",
                source_path="generated://shadow",
                status=HIDDEN_DATASET_STATUS,
            )
        )
        session.commit()

        visible = service.list_datasets()
        visible_names = [item.name for item in visible]
        assert "公开演示集" in visible_names
        assert "金融影子评测集" not in visible_names

        all_datasets = service.list_datasets(include_hidden=True)
        all_names = [item.name for item in all_datasets]
        assert "金融影子评测集" in all_names
