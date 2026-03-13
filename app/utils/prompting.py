from typing import Dict, Iterable

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


def sample_to_prompt_vars(sample) -> Dict[str, str]:
    return {
        "query": sample.query,
        "context": sample.context,
        "reference_answer": sample.reference_answer,
        "category": sample.category,
        "difficulty": sample.difficulty,
        "tags": ", ".join(sample.tags or []),
        "notes": sample.notes or "",
    }


def build_prompt_messages(prompt_version, sample) -> list:
    prompt_vars = sample_to_prompt_vars(sample)
    messages = []
    system_prompt = (prompt_version.system_prompt or "").strip()
    if system_prompt:
        system_template = ChatPromptTemplate.from_messages([("system", system_prompt)])
        messages.extend(system_template.invoke(prompt_vars).to_messages())

    for example in prompt_version.few_shot_examples or []:
        example_query = example.get("query", "")
        example_context = example.get("context", "")
        example_answer = example.get("answer", "")
        example_user = (
            "问题：{query}\n"
            "上下文：{context}\n"
            "请仅依据上下文作答。"
        ).format(query=example_query, context=example_context)
        messages.append(HumanMessage(content=example_user))
        messages.append(AIMessage(content=example_answer))

    user_template = ChatPromptTemplate.from_messages([("human", prompt_version.user_prompt_template)])
    messages.extend(user_template.invoke(prompt_vars).to_messages())
    return messages


def stringify_messages(messages: Iterable[BaseMessage]) -> str:
    rendered = []
    for message in messages:
        if isinstance(message, SystemMessage):
            role = "SYSTEM"
        elif isinstance(message, HumanMessage):
            role = "USER"
        elif isinstance(message, AIMessage):
            role = "ASSISTANT"
        else:
            role = message.type.upper()
        rendered.append("{role}:\n{content}".format(role=role, content=message.content))
    return "\n\n".join(rendered)
