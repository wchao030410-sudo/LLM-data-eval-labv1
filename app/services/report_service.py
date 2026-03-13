from collections import Counter
from datetime import datetime
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Dataset, EvaluationResult, EvaluationResultBadcaseTag, Experiment, ExperimentRun, PromptVersion
from app.utils.report_templates import build_report_filename, render_html_report, render_markdown_report


class ReportService:
    def __init__(self, session: Session):
        self.session = session

    def generate_prompt_comparison_report(
        self,
        dataset_id: int,
        prompt_version_a_id: int,
        prompt_version_b_id: int,
        output_format: str = "markdown",
    ) -> Dict:
        if output_format not in {"markdown", "html"}:
            raise ValueError("output_format 仅支持 markdown 或 html")

        dataset = self.session.get(Dataset, dataset_id)
        if not dataset:
            raise ValueError("Dataset not found")

        version_a = self._get_prompt_version(prompt_version_a_id)
        version_b = self._get_prompt_version(prompt_version_b_id)
        if prompt_version_a_id == prompt_version_b_id:
            raise ValueError("请选择两个不同的 Prompt 版本")

        run_a = self._get_latest_completed_run(dataset_id, prompt_version_a_id)
        run_b = self._get_latest_completed_run(dataset_id, prompt_version_b_id)
        if not run_a or not run_b:
            raise ValueError("两个 Prompt 版本都需要在当前数据集上至少有一次已完成的实验运行")

        results_a = self._load_result_map(run_a.id)
        results_b = self._load_result_map(run_b.id)
        paired_ids = sorted(set(results_a.keys()) & set(results_b.keys()))
        if not paired_ids:
            raise ValueError("两个 Prompt 版本没有可直接对比的样本结果")

        metric_fields = [
            ("overall_score", "总分"),
            ("correctness", "正确性"),
            ("completeness", "完整性"),
            ("groundedness", "基于上下文程度"),
            ("format_compliance", "格式符合度"),
            ("hallucination_risk", "幻觉率"),
        ]
        metric_rows = []
        for field, label in metric_fields:
            a_avg = sum(results_a[sid][field] for sid in paired_ids) / len(paired_ids)
            b_avg = sum(results_b[sid][field] for sid in paired_ids) / len(paired_ids)
            metric_rows.append({"label": label, "a": a_avg, "b": b_avg, "diff": b_avg - a_avg})

        badcase_counter_a = Counter(tag for sid in paired_ids for tag in results_a[sid]["badcase_tags"])
        badcase_counter_b = Counter(tag for sid in paired_ids for tag in results_b[sid]["badcase_tags"])
        all_badcase_tags = sorted(set(badcase_counter_a.keys()) | set(badcase_counter_b.keys()))
        badcase_rows = [
            {
                "tag": tag,
                "a": badcase_counter_a.get(tag, 0),
                "b": badcase_counter_b.get(tag, 0),
                "diff": badcase_counter_b.get(tag, 0) - badcase_counter_a.get(tag, 0),
            }
            for tag in all_badcase_tags
        ]

        category_map: Dict[str, List[float]] = {}
        for sid in paired_ids:
            category = results_a[sid]["category"]
            category_map.setdefault(category, [])
            category_map[category].append(results_b[sid]["overall_score"] - results_a[sid]["overall_score"])
        category_rows = []
        for category, deltas in category_map.items():
            a_scores = [results_a[sid]["overall_score"] for sid in paired_ids if results_a[sid]["category"] == category]
            b_scores = [results_b[sid]["overall_score"] for sid in paired_ids if results_b[sid]["category"] == category]
            category_rows.append(
                {
                    "category": category,
                    "a": sum(a_scores) / len(a_scores),
                    "b": sum(b_scores) / len(b_scores),
                    "delta": sum(deltas) / len(deltas),
                }
            )
        category_rows.sort(key=lambda item: item["delta"], reverse=True)
        top_improved = category_rows[0] if category_rows else {"category": "无", "delta": 0.0}
        top_declined = category_rows[-1] if category_rows else {"category": "无", "delta": 0.0}

        case_rows = self._build_case_rows(paired_ids, results_a, results_b)
        conclusions = self._build_conclusions(metric_rows, badcase_rows, top_improved, top_declined, version_a, version_b)

        report = {
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "dataset_name": dataset.name,
            "version_a": {"name": version_a.prompt.name, "version": version_a.version},
            "version_b": {"name": version_b.prompt.name, "version": version_b.version},
            "run_a": {"run_id": run_a.id, "run_name": run_a.run_name},
            "run_b": {"run_id": run_b.id, "run_name": run_b.run_name},
            "sample_count_a": len(results_a),
            "sample_count_b": len(results_b),
            "paired_sample_count": len(paired_ids),
            "metric_rows": metric_rows,
            "badcase_rows": badcase_rows,
            "category_rows": category_rows,
            "top_improved_category": top_improved,
            "top_declined_category": top_declined,
            "case_rows": case_rows,
            "conclusions": conclusions,
        }

        if output_format == "html":
            content = render_html_report(report)
            content_type = "text/html; charset=utf-8"
        else:
            content = render_markdown_report(report)
            content_type = "text/markdown; charset=utf-8"

        return {
            "filename": build_report_filename(report["version_a"], report["version_b"], output_format),
            "content_type": content_type,
            "content": content,
            "summary": {
                "dataset_name": report["dataset_name"],
                "paired_sample_count": report["paired_sample_count"],
                "avg_score_delta": next(item["diff"] for item in metric_rows if item["label"] == "总分"),
                "top_improved_category": top_improved["category"],
                "top_declined_category": top_declined["category"],
            },
        }

    def _get_prompt_version(self, version_id: int) -> PromptVersion:
        stmt = (
            select(PromptVersion)
            .options(selectinload(PromptVersion.prompt))
            .where(PromptVersion.id == version_id)
        )
        version = self.session.scalars(stmt).first()
        if not version:
            raise ValueError("Prompt 版本不存在")
        return version

    def _get_latest_completed_run(self, dataset_id: int, prompt_version_id: int):
        stmt = (
            select(ExperimentRun)
            .join(Experiment, Experiment.id == ExperimentRun.experiment_id)
            .where(
                Experiment.dataset_id == dataset_id,
                Experiment.prompt_version_id == prompt_version_id,
                ExperimentRun.run_status == "completed",
            )
            .order_by(ExperimentRun.created_at.desc())
        )
        return self.session.scalars(stmt).first()

    def _load_result_map(self, run_id: int) -> Dict[int, Dict]:
        stmt = (
            select(EvaluationResult)
            .options(
                selectinload(EvaluationResult.sample),
                selectinload(EvaluationResult.tag_links).selectinload(EvaluationResultBadcaseTag.badcase_tag),
            )
            .where(EvaluationResult.experiment_run_id == run_id)
        )
        result_map: Dict[int, Dict] = {}
        for item in self.session.scalars(stmt).all():
            result_map[item.sample_id] = {
                "sample_id": item.sample_id,
                "query": item.sample.query,
                "category": item.sample.category,
                "reference_answer": item.sample.reference_answer,
                "generated_answer": item.generated_answer,
                "overall_score": item.overall_score,
                "correctness": item.correctness,
                "completeness": item.completeness,
                "groundedness": item.groundedness,
                "format_compliance": item.format_compliance,
                "hallucination_risk": item.hallucination_risk,
                "badcase_tags": [link.badcase_tag.code for link in item.tag_links],
            }
        return result_map

    def _build_case_rows(self, paired_ids: List[int], results_a: Dict[int, Dict], results_b: Dict[int, Dict]) -> List[Dict]:
        scored_cases = []
        for sid in paired_ids:
            delta = results_b[sid]["overall_score"] - results_a[sid]["overall_score"]
            scored_cases.append(
                {
                    "query": results_a[sid]["query"],
                    "category": results_a[sid]["category"],
                    "reference_answer": results_a[sid]["reference_answer"],
                    "a_answer": results_a[sid]["generated_answer"],
                    "b_answer": results_b[sid]["generated_answer"],
                    "a_score": results_a[sid]["overall_score"],
                    "b_score": results_b[sid]["overall_score"],
                    "delta": delta,
                }
            )
        scored_cases.sort(key=lambda item: abs(item["delta"]), reverse=True)
        return scored_cases[:4]

    def _build_conclusions(self, metric_rows: List[Dict], badcase_rows: List[Dict], top_improved: Dict, top_declined: Dict, version_a, version_b) -> List[str]:
        total_delta = next(item["diff"] for item in metric_rows if item["label"] == "总分")
        hallucination_delta = next(item["diff"] for item in metric_rows if item["label"] == "幻觉率")
        conclusions = []
        if total_delta >= 0:
            conclusions.append("相较于 {a} / {av}，{b} / {bv} 在整体总分上更优，平均提升 {delta:.4f}。".format(
                a=version_a.prompt.name, av=version_a.version, b=version_b.prompt.name, bv=version_b.version, delta=total_delta
            ))
        else:
            conclusions.append("相较于 {a} / {av}，{b} / {bv} 在整体总分上出现回退，平均下降 {delta:.4f}。".format(
                a=version_a.prompt.name, av=version_a.version, b=version_b.prompt.name, bv=version_b.version, delta=abs(total_delta)
            ))
        if hallucination_delta <= 0:
            conclusions.append("B 版本的幻觉率变化为 {delta:+.4f}，风险控制更稳定。".format(delta=hallucination_delta))
        else:
            conclusions.append("B 版本的幻觉率变化为 {delta:+.4f}，建议进一步检查 groundedness 约束。".format(delta=hallucination_delta))
        conclusions.append("提升最明显的 category 是 {category}，下降最明显的 category 是 {declined}。".format(
            category=top_improved["category"], declined=top_declined["category"]
        ))
        increased_badcase = [row["tag"] for row in badcase_rows if row["diff"] > 0]
        if increased_badcase:
            conclusions.append("B 版本在 {tags} 等 Bad Case 标签上数量增加，建议回看对应样本与输出格式约束。".format(
                tags="、".join(increased_badcase[:3])
            ))
        else:
            conclusions.append("B 版本没有出现明显新增的 Bad Case 标签分布，整体风险相对可控。")
        return conclusions
