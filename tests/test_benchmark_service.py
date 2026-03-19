from types import SimpleNamespace
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.benchmark_service import BenchmarkService


def test_finance_investment_sample_triggers_manual_review_signals():
    service = BenchmarkService()
    sample = SimpleNamespace(
        query="这个基金最近收益怎么样，适合长期持有吗？",
        context="基金净值会随市场波动，过往表现不代表未来收益，投资前需评估自身风险承受能力。",
        reference_answer="基金收益存在波动，是否适合长期持有需要结合风险承受能力与投资目标判断。",
        category="投顾",
        difficulty="hard",
        tags=["finance", "fund"],
        notes="金融投资咨询场景。",
    )
    scores = {
        "correctness": 0.32,
        "completeness": 0.55,
        "groundedness": 0.28,
        "format_compliance": 0.82,
        "hallucination_risk": 0.74,
        "overall_score": 0.38,
    }

    context = service.build_context(sample, "这只基金稳赚不赔，可以长期持有。", scores)

    assert context["benchmark_profile"]["profile_name"] == "finance_investment_advisory"
    assert context["business_scorecard"]["risk_disclosure_required"] is True
    assert context["business_scorecard"]["financial_safety_score"] < 0.2
    assert context["manual_review"]["required"] is True
    assert "missing_risk_disclosure" in context["manual_review"]["reasons"]
    assert "financial_safety_risk" in context["manual_review"]["reasons"]
    assert context["data_production"]["training_priority"] == "p0"


def test_general_sample_uses_general_profile():
    service = BenchmarkService()
    sample = SimpleNamespace(
        query="什么是检索增强生成？",
        context="检索增强生成会先检索外部证据，再结合证据生成回答。",
        reference_answer="检索增强生成是先检索证据再生成回答的方法。",
        category="检索",
        difficulty="easy",
        tags=["rag"],
        notes="",
    )
    scores = {
        "correctness": 0.86,
        "completeness": 0.88,
        "groundedness": 0.84,
        "format_compliance": 0.76,
        "hallucination_risk": 0.12,
        "overall_score": 0.83,
    }

    context = service.build_context(sample, "检索增强生成是先检索证据，再基于证据回答。", scores)

    assert context["benchmark_profile"]["profile_name"] == "general_search_qa"
    assert context["business_scorecard"]["risk_disclosure_required"] is False
    assert context["manual_review"]["required"] is False
    assert context["data_production"]["training_priority"] == "p2"
