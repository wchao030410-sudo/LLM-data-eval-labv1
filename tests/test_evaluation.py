from types import SimpleNamespace
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.evaluation_service import Evaluator


def make_sample():
    return SimpleNamespace(
        query="什么是检索增强生成？",
        context="检索增强生成会先检索外部证据，再结合这些证据生成回答，从而提升事实性。",
        reference_answer="检索增强生成是先检索证据，再基于证据生成回答的方法。",
    )


def test_rule_based_scores_high_for_grounded_answer():
    service = Evaluator()
    sample = make_sample()
    result = service.evaluate(sample, "检索增强生成是先检索证据，再基于证据生成回答的方法。")
    assert result["correctness"] > 0.5
    assert result["groundedness"] > 0.5
    assert result["overall_score"] > 0.6


def test_build_judge_prompt_contains_core_fields():
    service = Evaluator()
    sample = make_sample()
    prompt = service.build_judge_prompt(sample, "这是一个测试回答。", benchmark_focus="Benchmark profile: 通用搜索问答基准")
    assert "Question:" in prompt
    assert "Context:" in prompt
    assert "Candidate answer:" in prompt
    assert "Additional benchmark guidance:" in prompt
