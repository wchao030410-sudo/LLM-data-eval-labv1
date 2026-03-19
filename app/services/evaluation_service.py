from typing import Dict, Optional

from app.utils.scoring import format_compliance_score, groundedness_ratio, token_overlap_ratio


class Evaluator:
    def evaluate(self, sample, generated_answer: str) -> Dict:
        reference = sample.reference_answer or ""
        context = sample.context or ""
        generated = (generated_answer or "").strip()

        correctness = token_overlap_ratio(generated, reference)
        completeness = min(1.0, len(generated.split()) / max(len(reference.split()), 1))
        groundedness = groundedness_ratio(generated, context)
        format_compliance = format_compliance_score(generated)
        hallucination_risk = max(0.0, min(1.0, 1 - groundedness * 0.75 - correctness * 0.25))
        overall_score = (
            correctness * 0.30
            + completeness * 0.20
            + groundedness * 0.25
            + format_compliance * 0.10
            + (1 - hallucination_risk) * 0.15
        )

        return {
            "correctness": round(correctness, 4),
            "completeness": round(completeness, 4),
            "groundedness": round(groundedness, 4),
            "format_compliance": round(format_compliance, 4),
            "hallucination_risk": round(hallucination_risk, 4),
            "overall_score": round(overall_score, 4),
        }

    def build_judge_prompt(self, sample, generated_answer: str, benchmark_focus: Optional[str] = None) -> str:
        prompt = (
            "Evaluate the following search QA answer.\n"
            "Question: {query}\n"
            "Context: {context}\n"
            "Reference answer: {reference}\n"
            "Candidate answer: {candidate}\n\n"
            "Score correctness, completeness, groundedness, format compliance, hallucination risk, and overall score."
        ).format(
            query=sample.query,
            context=sample.context,
            reference=sample.reference_answer,
            candidate=generated_answer,
        )
        if benchmark_focus:
            prompt += "\n\nAdditional benchmark guidance:\n{guidance}".format(guidance=benchmark_focus)
        return prompt
