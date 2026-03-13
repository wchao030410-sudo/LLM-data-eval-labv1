from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
import streamlit as st


class APIError(RuntimeError):
    pass


class APIClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    def _request(self, method: str, path: str, **kwargs):
        url = "{base}{path}".format(base=self.base_url, path=path)
        try:
            response = requests.request(method, url, timeout=120, **kwargs)
        except requests.RequestException as exc:
            raise APIError(str(exc))
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise APIError("{code}: {detail}".format(code=response.status_code, detail=detail))
        if response.text:
            return response.json()
        return None

    def health(self):
        return self._request("GET", "/health")

    def analysis_overview(self):
        return self._request("GET", "/analysis/overview")

    def analysis_runs(self):
        return self._request("GET", "/analysis/runs")

    def list_datasets(self):
        return self._request("GET", "/datasets")

    def create_dataset(self, payload: Dict):
        return self._request("POST", "/datasets", json=payload)

    def list_samples(self, dataset_id: int, search: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None):
        params = {"search": search, "category": category, "difficulty": difficulty}
        params = {key: value for key, value in params.items() if value}
        return self._request("GET", "/datasets/{dataset_id}/samples".format(dataset_id=dataset_id), params=params)

    def import_samples(self, dataset_id: int, file_path: str):
        return self._request("POST", "/datasets/import", json={"dataset_id": dataset_id, "file_path": file_path})

    def list_prompts(self):
        return self._request("GET", "/prompts")

    def list_prompt_versions(self, prompt_id: int):
        return self._request("GET", "/prompts/{prompt_id}/versions".format(prompt_id=prompt_id))

    def get_prompt_version(self, version_id: int):
        return self._request("GET", "/prompt-versions/{version_id}".format(version_id=version_id))

    def list_experiments(self):
        return self._request("GET", "/experiments")

    def create_experiment(self, payload: Dict):
        return self._request("POST", "/experiments", json=payload)

    def get_experiment(self, experiment_id: int):
        return self._request("GET", "/experiments/{experiment_id}".format(experiment_id=experiment_id))

    def run_experiment(self, experiment_id: int, run_name: Optional[str] = None):
        return self._request("POST", "/experiments/{experiment_id}/run".format(experiment_id=experiment_id), json={"run_name": run_name})

    def list_runs(self):
        return self._request("GET", "/experiment-runs")

    def get_run(self, run_id: int):
        return self._request("GET", "/experiment-runs/{run_id}".format(run_id=run_id))

    def get_run_results(self, run_id: int):
        return self._request("GET", "/experiment-runs/{run_id}/results".format(run_id=run_id))

    def export_prompt_comparison_report(self, payload: Dict):
        return self._request("POST", "/reports/compare-prompt-versions", json=payload)


@st.cache_data(show_spinner=False, ttl=30)
def cached_datasets(base_url: str):
    return APIClient().list_datasets()


@st.cache_data(show_spinner=False, ttl=30)
def cached_prompts(base_url: str):
    client = APIClient()
    prompts = client.list_prompts()
    version_map = {}
    for prompt in prompts:
        version_map[prompt["id"]] = client.list_prompt_versions(prompt["id"])
    return prompts, version_map


@st.cache_data(show_spinner=False, ttl=30)
def cached_runs(base_url: str):
    return APIClient().list_runs()


@st.cache_data(show_spinner=False, ttl=30)
def build_results_dataframe(base_url: str) -> pd.DataFrame:
    client = APIClient()
    runs = client.list_runs()
    experiments = {item["id"]: item for item in client.list_experiments()}
    prompts, version_map = cached_prompts(base_url)
    prompt_lookup = {}
    for prompt in prompts:
        for version in version_map.get(prompt["id"], []):
            prompt_lookup[version["id"]] = {
                "prompt_name": prompt["name"],
                "prompt_version": version["version"],
            }

    rows: List[Dict] = []
    sample_cache: Dict[int, Dict] = {}
    for run in runs:
        experiment = experiments.get(run["experiment_id"])
        if not experiment:
            continue
        dataset_id = experiment["dataset_id"]
        if dataset_id not in sample_cache:
            sample_cache[dataset_id] = {
                item["id"]: item for item in client.list_samples(dataset_id)
            }
        sample_lookup = sample_cache[dataset_id]
        prompt_meta = prompt_lookup.get(experiment["prompt_version_id"], {})
        for result in client.get_run_results(run["id"]):
            sample = sample_lookup.get(result["sample_id"], {})
            rows.append(
                {
                    "run_id": run["id"],
                    "run_name": run["run_name"],
                    "experiment_id": experiment["id"],
                    "dataset_id": dataset_id,
                    "sample_id": result["sample_id"],
                    "query": sample.get("query", ""),
                    "context": sample.get("context", ""),
                    "reference_answer": sample.get("reference_answer", ""),
                    "category": sample.get("category", "unknown"),
                    "difficulty": sample.get("difficulty", "unknown"),
                    "tags": sample.get("tags", []),
                    "generated_answer": result["generated_answer"],
                    "overall_score": result["overall_score"],
                    "correctness": result["correctness"],
                    "completeness": result["completeness"],
                    "groundedness": result["groundedness"],
                    "format_compliance": result["format_compliance"],
                    "hallucination_risk": result["hallucination_risk"],
                    "badcase_tags": result.get("badcase_tags", []),
                    "prompt_name": prompt_meta.get("prompt_name", "unknown"),
                    "prompt_version": prompt_meta.get("prompt_version", "unknown"),
                }
            )
    return pd.DataFrame(rows)


def save_uploaded_file(uploaded_file, upload_dir: str) -> str:
    target_dir = Path(upload_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / uploaded_file.name
    file_path.write_bytes(uploaded_file.getbuffer())
    return str(file_path.resolve())
