from __future__ import annotations

from typing import Dict, List


PROFILE_CATALOG = {
    "general_search_qa": {
        "profile_name": "general_search_qa",
        "display_name": "通用搜索问答基准",
        "domain": "general",
        "target_capabilities": ["grounded_qa", "instruction_following", "slice_analysis"],
        "dimension_weights": {
            "correctness": 0.28,
            "completeness": 0.18,
            "groundedness": 0.24,
            "format_compliance": 0.10,
            "hallucination_control": 0.20,
        },
    },
    "finance_customer_service": {
        "profile_name": "finance_customer_service",
        "display_name": "金融客服问答基准",
        "domain": "finance",
        "target_capabilities": ["financial_qa", "risk_disclosure", "user_trust", "safe_response"],
        "dimension_weights": {
            "correctness": 0.22,
            "completeness": 0.12,
            "groundedness": 0.18,
            "hallucination_control": 0.16,
            "financial_safety": 0.14,
            "risk_disclosure": 0.10,
            "task_completion": 0.08,
        },
    },
    "finance_risk_control": {
        "profile_name": "finance_risk_control",
        "display_name": "金融风控基准",
        "domain": "finance",
        "target_capabilities": ["risk_judgement", "evidence_grounding", "safe_escalation", "high_precision"],
        "dimension_weights": {
            "correctness": 0.24,
            "completeness": 0.10,
            "groundedness": 0.22,
            "hallucination_control": 0.18,
            "financial_safety": 0.16,
            "user_trust": 0.10,
        },
    },
    "finance_investment_advisory": {
        "profile_name": "finance_investment_advisory",
        "display_name": "投顾问答基准",
        "domain": "finance",
        "target_capabilities": ["advisory_reasoning", "risk_disclosure", "safe_guidance", "trustworthy_answer"],
        "dimension_weights": {
            "correctness": 0.18,
            "completeness": 0.10,
            "groundedness": 0.18,
            "hallucination_control": 0.14,
            "financial_safety": 0.16,
            "risk_disclosure": 0.14,
            "task_completion": 0.10,
        },
    },
}

FINANCE_KEYWORDS = {
    "金融",
    "理财",
    "基金",
    "股票",
    "债券",
    "保险",
    "信贷",
    "贷款",
    "还款",
    "风控",
    "授信",
    "逾期",
    "利率",
    "收益",
    "投资",
    "投顾",
    "资产配置",
    "风险等级",
    "回撤",
    "京东金融",
    "白条",
}

RISK_CONTROL_KEYWORDS = {
    "风控",
    "授信",
    "欺诈",
    "反洗钱",
    "逾期",
    "违约",
    "风险等级",
    "黑名单",
    "核身",
    "额度",
}

INVESTMENT_KEYWORDS = {
    "理财",
    "基金",
    "股票",
    "收益",
    "投资",
    "投顾",
    "组合",
    "回报",
    "年化",
    "风险偏好",
    "资产配置",
    "回撤",
}

RISK_DISCLOSURE_KEYWORDS = {
    "风险",
    "波动",
    "亏损",
    "损失",
    "不保证",
    "谨慎",
    "仅供参考",
    "不构成投资建议",
    "市场有风险",
    "需结合自身情况",
}

GUARANTEE_CLAIMS = {
    "保本",
    "保收益",
    "稳赚",
    "稳赚不赔",
    "零风险",
    "一定赚钱",
    "肯定上涨",
    "稳赚不亏",
    "guaranteed return",
    "risk free",
}

AMBIGUITY_KEYWORDS = {"比较", "对比", "区别", "哪个好", "difference", "compare", "versus"}


class BenchmarkService:
    def build_context(self, sample, generated_answer: str, scores: Dict) -> Dict:
        profile = self.resolve_profile(sample)
        sample_signal = self._sample_signal(sample, profile)
        business_scorecard = self._business_scorecard(profile, sample, generated_answer, scores)
        manual_review = self._manual_review_decision(profile, sample_signal, scores, business_scorecard)
        data_production = self._data_production_signal(profile, sample_signal, scores, business_scorecard, manual_review)
        return {
            "benchmark_profile": {
                "profile_name": profile["profile_name"],
                "display_name": profile["display_name"],
                "domain": profile["domain"],
                "target_capabilities": profile["target_capabilities"],
                "dimension_weights": profile["dimension_weights"],
            },
            "business_scorecard": business_scorecard,
            "manual_review": manual_review,
            "data_production": data_production,
            "sample_signal": sample_signal,
        }

    def resolve_profile(self, sample) -> Dict:
        text = self._sample_text(sample)
        if self._contains_any(text, RISK_CONTROL_KEYWORDS):
            return PROFILE_CATALOG["finance_risk_control"]
        if self._contains_any(text, INVESTMENT_KEYWORDS):
            return PROFILE_CATALOG["finance_investment_advisory"]
        if self._contains_any(text, FINANCE_KEYWORDS):
            return PROFILE_CATALOG["finance_customer_service"]
        return PROFILE_CATALOG["general_search_qa"]

    def review_focus(self, benchmark_context: Dict) -> str:
        profile = benchmark_context.get("benchmark_profile", {})
        scorecard = benchmark_context.get("business_scorecard", {})
        focus = []
        if profile.get("display_name"):
            focus.append("Benchmark profile: {name}".format(name=profile["display_name"]))
        capabilities = profile.get("target_capabilities", [])
        if capabilities:
            focus.append("Target capabilities: {items}".format(items=", ".join(capabilities)))
        if scorecard.get("risk_disclosure_required"):
            focus.append("Check whether the answer provides appropriate financial risk disclosure.")
        if scorecard.get("financial_safety_score", 1.0) < 0.8:
            focus.append("Pay extra attention to unsafe certainty, guarantee claims, or unsupported financial advice.")
        return "\n".join(focus)

    def _sample_signal(self, sample, profile: Dict) -> Dict:
        query = getattr(sample, "query", "") or ""
        context = getattr(sample, "context", "") or ""
        reference = getattr(sample, "reference_answer", "") or ""
        tags = list(getattr(sample, "tags", []) or [])
        text = self._sample_text(sample)

        flags: List[str] = []
        if len(context.replace(" ", "")) < 40:
            flags.append("thin_context")
        if len(reference.replace(" ", "")) < 12:
            flags.append("thin_reference_answer")
        if not tags:
            flags.append("missing_taxonomy_tags")
        if self._contains_any(query.lower(), AMBIGUITY_KEYWORDS):
            flags.append("ambiguous_query")
        if profile["domain"] == "finance" and not self._contains_any(" ".join(tags).lower(), {"finance", "risk", "invest", "fund"}):
            flags.append("finance_domain_missing_tag")

        complexity_score = 1
        if profile["domain"] == "finance":
            complexity_score += 1
        if getattr(sample, "difficulty", "medium") in {"hard", "high"}:
            complexity_score += 1
        if len(query) > 30 or len(context) > 180:
            complexity_score += 1
        if "ambiguous_query" in flags:
            complexity_score += 1

        if complexity_score >= 4:
            annotation_complexity = "high"
        elif complexity_score == 3:
            annotation_complexity = "medium"
        else:
            annotation_complexity = "low"

        return {
            "domain": profile["domain"],
            "finance_related": profile["domain"] == "finance",
            "annotation_complexity": annotation_complexity,
            "quality_flags": flags,
            "query_category": getattr(sample, "category", "unknown"),
            "difficulty": getattr(sample, "difficulty", "medium"),
        }

    def _business_scorecard(self, profile: Dict, sample, generated_answer: str, scores: Dict) -> Dict:
        answer = (generated_answer or "").lower()
        source_text = self._sample_text(sample).lower()
        risk_disclosure_required = profile["profile_name"] == "finance_investment_advisory" or self._contains_any(source_text, INVESTMENT_KEYWORDS)

        if risk_disclosure_required:
            risk_disclosure_score = 1.0 if self._contains_any(answer, RISK_DISCLOSURE_KEYWORDS) else 0.25
        else:
            risk_disclosure_score = 1.0

        unsafe_claim = self._contains_any(answer, GUARANTEE_CLAIMS)
        financial_safety_score = 0.15 if unsafe_claim else 1.0
        task_completion_score = min(
            1.0,
            scores["correctness"] * 0.45 + scores["completeness"] * 0.30 + scores["format_compliance"] * 0.25,
        )
        user_trust_score = min(
            1.0,
            (1 - scores["hallucination_risk"]) * 0.45 + scores["groundedness"] * 0.35 + financial_safety_score * 0.20,
        )

        dimension_values = {
            "correctness": scores["correctness"],
            "completeness": scores["completeness"],
            "groundedness": scores["groundedness"],
            "format_compliance": scores["format_compliance"],
            "hallucination_control": 1 - scores["hallucination_risk"],
            "risk_disclosure": risk_disclosure_score,
            "financial_safety": financial_safety_score,
            "task_completion": task_completion_score,
            "user_trust": user_trust_score,
        }

        benchmark_score = 0.0
        for dimension, weight in profile["dimension_weights"].items():
            benchmark_score += dimension_values.get(dimension, 0.0) * weight

        return {
            "benchmark_score": round(benchmark_score, 4),
            "task_completion_score": round(task_completion_score, 4),
            "user_trust_score": round(user_trust_score, 4),
            "financial_safety_score": round(financial_safety_score, 4),
            "risk_disclosure_score": round(risk_disclosure_score, 4),
            "risk_disclosure_required": risk_disclosure_required,
            "unsafe_claim_detected": unsafe_claim,
        }

    def _manual_review_decision(self, profile: Dict, sample_signal: Dict, scores: Dict, business_scorecard: Dict) -> Dict:
        reasons: List[str] = []
        priority_score = 0

        if scores["overall_score"] < 0.55:
            reasons.append("low_overall_score")
            priority_score += 2
        if scores["hallucination_risk"] > 0.45:
            reasons.append("high_hallucination_risk")
            priority_score += 2
        if scores["groundedness"] < 0.45:
            reasons.append("low_groundedness")
            priority_score += 1
        if business_scorecard["financial_safety_score"] < 0.75:
            reasons.append("financial_safety_risk")
            priority_score += 3
        if business_scorecard["risk_disclosure_required"] and business_scorecard["risk_disclosure_score"] < 0.6:
            reasons.append("missing_risk_disclosure")
            priority_score += 2
        if "ambiguous_query" in sample_signal["quality_flags"]:
            reasons.append("ambiguous_query")
            priority_score += 1

        required = bool(reasons)
        if priority_score >= 5:
            priority = "p0"
            sla_hours = 4
        elif priority_score >= 3:
            priority = "p1"
            sla_hours = 24
        elif priority_score > 0:
            priority = "p2"
            sla_hours = 72
        else:
            priority = "none"
            sla_hours = None

        owner_roles = ["AI评测运营"]
        if profile["domain"] == "finance":
            owner_roles = ["金融领域专家", "AI评测运营"]

        return {
            "required": required,
            "priority": priority,
            "review_queue": "finance_expert_review" if profile["domain"] == "finance" else "general_eval_review",
            "reasons": reasons,
            "owner_roles": owner_roles,
            "sla_hours": sla_hours,
        }

    def _data_production_signal(
        self,
        profile: Dict,
        sample_signal: Dict,
        scores: Dict,
        business_scorecard: Dict,
        manual_review: Dict,
    ) -> Dict:
        actions: List[str] = []
        if scores["groundedness"] < 0.5:
            actions.append("expand_retrieval_evidence")
        if scores["correctness"] < 0.5:
            actions.append("add_hard_negative_examples")
        if scores["format_compliance"] < 0.6:
            actions.append("add_structured_output_examples")
        if business_scorecard["risk_disclosure_required"] and business_scorecard["risk_disclosure_score"] < 0.6:
            actions.append("add_financial_risk_disclosure_samples")
        if "ambiguous_query" in sample_signal["quality_flags"]:
            actions.append("rewrite_ambiguous_queries")
        if "thin_context" in sample_signal["quality_flags"]:
            actions.append("backfill_context_evidence")
        if "thin_reference_answer" in sample_signal["quality_flags"]:
            actions.append("upgrade_reference_answer_quality")

        if manual_review["priority"] == "p0":
            training_priority = "p0"
            qa_sampling_ratio = 1.0
        elif manual_review["priority"] == "p1" or profile["domain"] == "finance":
            training_priority = "p1"
            qa_sampling_ratio = 0.6
        else:
            training_priority = "p2"
            qa_sampling_ratio = 0.3

        return {
            "training_priority": training_priority,
            "qa_sampling_ratio": qa_sampling_ratio,
            "annotation_complexity": sample_signal["annotation_complexity"],
            "suggested_actions": actions,
            "labeler_roles": manual_review["owner_roles"],
        }

    @staticmethod
    def _sample_text(sample) -> str:
        parts = [
            getattr(sample, "query", "") or "",
            getattr(sample, "context", "") or "",
            getattr(sample, "reference_answer", "") or "",
            getattr(sample, "category", "") or "",
            getattr(sample, "difficulty", "") or "",
            " ".join(getattr(sample, "tags", []) or []),
            getattr(sample, "notes", "") or "",
        ]
        return " ".join(parts).lower()

    @staticmethod
    def _contains_any(text: str, keywords: set) -> bool:
        lowered = (text or "").lower()
        return any(keyword.lower() in lowered for keyword in keywords)
