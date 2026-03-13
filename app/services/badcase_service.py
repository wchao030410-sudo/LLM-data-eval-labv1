from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BadcaseTag, EvaluationResultBadcaseTag
from app.utils.demo_data import DEFAULT_BADCASE_TAGS


class BadcaseService:
    def __init__(self, session: Session):
        self.session = session

    def ensure_default_tags(self) -> list:
        existing_tags = {
            tag.code: tag for tag in self.session.scalars(select(BadcaseTag)).all()
        }
        created = []
        for item in DEFAULT_BADCASE_TAGS:
            if item["code"] in existing_tags:
                tag = existing_tags[item["code"]]
                tag.name = item["name"]
                tag.description = item["description"]
                tag.severity = item["severity"]
            else:
                tag = BadcaseTag(**item)
                self.session.add(tag)
                created.append(tag)
        self.session.flush()
        return created

    def infer_tag_codes(self, sample, generated_answer: str, scores: Dict) -> List[str]:
        tags = []
        if scores["groundedness"] < 0.45:
            tags.append("hallucination")
        if scores["completeness"] < 0.70:
            tags.append("incomplete_answer")
        if scores["format_compliance"] < 0.60:
            tags.append("format_error")
        if scores["correctness"] < 0.45:
            tags.append("instruction_following_failure")
        if len((sample.context or "").replace(" ", "")) < 30:
            tags.append("insufficient_context")
        query_lower = (sample.query or "").lower()
        if any(token in query_lower for token in ["difference", "compare", "versus", "区别", "比较", "对比"]):
            tags.append("ambiguous_query")
        answer_text = generated_answer or ""
        if ("insufficient" in answer_text.lower() and "context" in answer_text.lower()) or ("上下文不足" in answer_text):
            tags.append("insufficient_context")
        return sorted(set(tags))

    def attach_tags(self, evaluation_result, tag_codes: List[str]) -> List[str]:
        if not tag_codes:
            evaluation_result.is_bad_case = False
            return []
        tag_map = {
            tag.code: tag for tag in self.session.scalars(select(BadcaseTag).where(BadcaseTag.code.in_(tag_codes))).all()
        }
        for code in tag_codes:
            tag = tag_map.get(code)
            if not tag:
                continue
            link = EvaluationResultBadcaseTag(
                evaluation_result_id=evaluation_result.id,
                badcase_tag_id=tag.id,
            )
            self.session.add(link)
        evaluation_result.is_bad_case = True
        self.session.flush()
        return list(tag_map.keys())
