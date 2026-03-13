from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import engine, get_db
from app.models import Base
from app.schemas.dataset import DatasetCreate, DatasetImportRequest, DatasetRead, DatasetUpdate, SampleCreate, SampleRead, SampleUpdate
from app.schemas.evaluation import EvaluationResultRead, RunSummaryRead
from app.schemas.experiment import ExperimentCreate, ExperimentRead, ExperimentRunRead, ExperimentRunRequest, ExperimentUpdate
from app.schemas.prompt import PromptCreate, PromptRead, PromptUpdate, PromptVersionCreate, PromptVersionRead, PromptVersionUpdate
from app.schemas.report import ReportCompareRequest, ReportExportResponse
from app.services import AnalysisService, DatasetService, ExperimentService, PromptService, ReportService

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.2.0")


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "description": "Search QA LLM evaluation and prompt optimization backend",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datasets", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)):
    return DatasetService(db).list_datasets()


@app.post("/datasets", response_model=DatasetRead)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    return DatasetService(db).create_dataset(payload)


@app.get("/datasets/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = DatasetService(db).get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@app.patch("/datasets/{dataset_id}", response_model=DatasetRead)
def update_dataset(dataset_id: int, payload: DatasetUpdate, db: Session = Depends(get_db)):
    try:
        return DatasetService(db).update_dataset(dataset_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    try:
        DatasetService(db).delete_dataset(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"deleted": True}


@app.get("/datasets/{dataset_id}/samples", response_model=list[SampleRead])
def list_samples(
    dataset_id: int,
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    difficulty: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return DatasetService(db).list_samples(dataset_id, search=search, category=category, difficulty=difficulty)


@app.post("/datasets/{dataset_id}/samples", response_model=SampleRead)
def create_sample(dataset_id: int, payload: SampleCreate, db: Session = Depends(get_db)):
    service = DatasetService(db)
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return service.create_sample(dataset_id, payload)


@app.patch("/samples/{sample_id}", response_model=SampleRead)
def update_sample(sample_id: int, payload: SampleUpdate, db: Session = Depends(get_db)):
    try:
        return DatasetService(db).update_sample(sample_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/datasets/import")
def import_dataset_samples(payload: DatasetImportRequest, db: Session = Depends(get_db)):
    service = DatasetService(db)
    if not service.get_dataset(payload.dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    try:
        inserted = service.import_samples_from_file(payload.dataset_id, payload.file_path)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"inserted": inserted}


@app.get("/prompts", response_model=list[PromptRead])
def list_prompts(db: Session = Depends(get_db)):
    return PromptService(db).list_prompts()


@app.post("/prompts", response_model=PromptRead)
def create_prompt(payload: PromptCreate, db: Session = Depends(get_db)):
    return PromptService(db).create_prompt(payload)


@app.patch("/prompts/{prompt_id}", response_model=PromptRead)
def update_prompt(prompt_id: int, payload: PromptUpdate, db: Session = Depends(get_db)):
    try:
        return PromptService(db).update_prompt(prompt_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersionRead])
def list_prompt_versions(prompt_id: int, db: Session = Depends(get_db)):
    return PromptService(db).list_versions(prompt_id=prompt_id)


@app.post("/prompts/{prompt_id}/versions", response_model=PromptVersionRead)
def create_prompt_version(prompt_id: int, payload: PromptVersionCreate, db: Session = Depends(get_db)):
    if payload.prompt_id != prompt_id:
        raise HTTPException(status_code=400, detail="prompt_id in body must match path")
    try:
        return PromptService(db).create_prompt_version(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/prompt-versions/{version_id}", response_model=PromptVersionRead)
def get_prompt_version(version_id: int, db: Session = Depends(get_db)):
    version = PromptService(db).get_prompt_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return version


@app.patch("/prompt-versions/{version_id}", response_model=PromptVersionRead)
def update_prompt_version(version_id: int, payload: PromptVersionUpdate, db: Session = Depends(get_db)):
    try:
        return PromptService(db).update_prompt_version(version_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/experiments", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)):
    return ExperimentService(db).list_experiments()


@app.post("/experiments", response_model=ExperimentRead)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    return ExperimentService(db).create_experiment(payload)


@app.get("/experiments/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    experiment = ExperimentService(db).get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@app.patch("/experiments/{experiment_id}", response_model=ExperimentRead)
def update_experiment(experiment_id: int, payload: ExperimentUpdate, db: Session = Depends(get_db)):
    try:
        return ExperimentService(db).update_experiment(experiment_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/experiments/{experiment_id}/run", response_model=ExperimentRunRead)
def run_experiment(experiment_id: int, payload: ExperimentRunRequest, db: Session = Depends(get_db)):
    try:
        return ExperimentService(db).run_experiment(experiment_id, run_name=payload.run_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/experiment-runs", response_model=list[ExperimentRunRead])
def list_runs(db: Session = Depends(get_db)):
    return ExperimentService(db).list_runs()


@app.get("/experiment-runs/{run_id}", response_model=ExperimentRunRead)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = ExperimentService(db).get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/experiment-runs/{run_id}/results", response_model=list[EvaluationResultRead])
def get_run_results(run_id: int, db: Session = Depends(get_db)):
    return ExperimentService(db).get_results(run_id)


@app.get("/analysis/overview")
def analysis_overview(db: Session = Depends(get_db)):
    return AnalysisService(db).overview()


@app.get("/analysis/runs", response_model=list[RunSummaryRead])
def analysis_runs(db: Session = Depends(get_db)):
    return AnalysisService(db).list_run_summaries()


@app.post("/reports/compare-prompt-versions", response_model=ReportExportResponse)
def export_prompt_comparison_report(payload: ReportCompareRequest, db: Session = Depends(get_db)):
    try:
        return ReportService(db).generate_prompt_comparison_report(
            dataset_id=payload.dataset_id,
            prompt_version_a_id=payload.prompt_version_a_id,
            prompt_version_b_id=payload.prompt_version_b_id,
            output_format=payload.output_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
