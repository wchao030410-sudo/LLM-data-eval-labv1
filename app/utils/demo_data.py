from typing import Dict, List


DEFAULT_BADCASE_TAGS = [
    {
        "code": "insufficient_context",
        "name": "上下文不足",
        "description": "提供的上下文证据不足，无法安全作答。",
        "severity": "medium",
    },
    {
        "code": "hallucination",
        "name": "幻觉",
        "description": "回答包含超出上下文证据范围的不支持信息。",
        "severity": "high",
    },
    {
        "code": "incomplete_answer",
        "name": "回答不完整",
        "description": "回答部分正确，但遗漏了关键事实或条件。",
        "severity": "medium",
    },
    {
        "code": "format_error",
        "name": "格式错误",
        "description": "回答未遵循指定的输出格式要求。",
        "severity": "low",
    },
    {
        "code": "instruction_following_failure",
        "name": "指令遵循失败",
        "description": "回答未遵守 Prompt 中的明确要求或约束。",
        "severity": "high",
    },
    {
        "code": "ambiguous_query",
        "name": "问题存在歧义",
        "description": "问题表达不够明确，容易导致检索或回答偏差。",
        "severity": "medium",
    },
]


def get_demo_samples() -> List[Dict]:
    return [
        {"query": "什么是检索增强生成？", "context": "检索增强生成会先从外部知识库中检索相关文档，再结合这些证据进行回答生成，从而提升答案的事实性。", "reference_answer": "检索增强生成是先检索外部证据，再基于证据生成回答的方法。", "category": "检索", "difficulty": "easy", "tags": ["RAG", "grounding"], "notes": "基础概念样本。"},
        {"query": "为什么切分粒度会影响检索效果？", "context": "文本切分粒度会影响召回颗粒度、上下文完整性和向量表达质量。切得太细会丢失上下文，切得太粗会降低检索精度。", "reference_answer": "切分粒度会影响召回精度、上下文完整性和向量表示质量。", "category": "检索", "difficulty": "medium", "tags": ["切分", "检索"], "notes": ""},
        {"query": "什么是稠密检索？", "context": "稠密检索会把问题和文档编码成向量，通过向量相似度来排序候选结果。", "reference_answer": "稠密检索是通过向量相似度来检索文档的方法。", "category": "检索", "difficulty": "easy", "tags": ["向量", "检索"], "notes": ""},
        {"query": "什么是稀疏检索？", "context": "稀疏检索依赖关键词匹配，例如 BM25，会使用词频和逆文档频率等信号进行排序。", "reference_answer": "稀疏检索是基于关键词匹配和统计信号进行检索的方法。", "category": "检索", "difficulty": "easy", "tags": ["BM25", "检索"], "notes": ""},
        {"query": "什么时候需要使用重排模型？", "context": "重排模型通常用在初步召回之后，用更强的相关性模型对候选结果重新排序，以提高前几条结果的质量。", "reference_answer": "重排模型适合在初步召回后提升头部结果的相关性。", "category": "检索", "difficulty": "medium", "tags": ["重排", "Search"], "notes": ""},
        {"query": "查询改写为什么对 Search QA 有帮助？", "context": "查询改写可以补充缺失关键词、统一表达方式、消除口语化噪声，从而提升检索召回率。", "reference_answer": "查询改写通过优化用户问题表达来提升检索召回率。", "category": "查询理解", "difficulty": "medium", "tags": ["改写", "Search"], "notes": ""},
        {"query": "什么是 groundedness？", "context": "groundedness 用来衡量回答是否由给定上下文支持，而不是由模型自行补充或臆造。", "reference_answer": "groundedness 指回答是否被提供的上下文证据支持。", "category": "评测", "difficulty": "easy", "tags": ["groundedness", "指标"], "notes": ""},
        {"query": "平台中的 hallucination risk 是怎么定义的？", "context": "hallucination risk 是一个启发式风险指标，用来估计回答中是否存在超出上下文证据范围的信息。", "reference_answer": "hallucination risk 用于估计回答中不受上下文支持的信息风险。", "category": "评测", "difficulty": "easy", "tags": ["hallucination", "指标"], "notes": ""},
        {"query": "为什么离线评测需要 reference answer？", "context": "reference answer 可以作为 correctness 和 completeness 的对照目标，帮助团队离线比较不同实验版本。", "reference_answer": "reference answer 为离线评测提供正确性和完整性的参照。", "category": "评测", "difficulty": "easy", "tags": ["reference", "离线评测"], "notes": ""},
        {"query": "format compliance 评测的是什么？", "context": "format compliance 用来评估回答是否满足预设输出格式，比如 JSON、要点列表或固定字段结构。", "reference_answer": "format compliance 评估回答是否符合指定输出格式。", "category": "评测", "difficulty": "easy", "tags": ["格式", "指标"], "notes": ""},
        {"query": "什么样的输出可以被视为 Bad Case？", "context": "Bad Case 指低质量模型输出，常见表现包括不正确、不完整、不 grounded 或没有遵循指令。", "reference_answer": "Bad Case 是在关键质量维度上表现不佳的模型输出。", "category": "分析", "difficulty": "easy", "tags": ["Bad Case", "分析"], "notes": ""},
        {"query": "为什么要对 Bad Case 做聚类？", "context": "对 Bad Case 做聚类有助于发现重复失败模式，帮助团队判断该优先优化 Prompt、数据还是检索策略。", "reference_answer": "Bad Case 聚类有助于识别重复失败模式并确定优化优先级。", "category": "分析", "difficulty": "medium", "tags": ["聚类", "归因"], "notes": ""},
        {"query": "问题存在歧义为什么会影响 Search QA？", "context": "问题有歧义时，检索系统可能会返回多个方向的证据，导致最终回答不完整或偏题。", "reference_answer": "歧义问题会导致检索证据不集中，从而影响回答质量。", "category": "查询理解", "difficulty": "medium", "tags": ["歧义", "Search"], "notes": ""},
        {"query": "什么是指令遵循失败？", "context": "当模型没有按要求输出指定格式，或者没有遵循“仅基于上下文回答”等约束时，就属于指令遵循失败。", "reference_answer": "指令遵循失败是模型没有遵守明确输出要求或约束。", "category": "分析", "difficulty": "medium", "tags": ["指令遵循", "错误"], "notes": ""},
        {"query": "为什么要追踪 Prompt 版本？", "context": "追踪 Prompt 版本可以帮助团队复现实验、比较版本差异，并理解性能变化来自哪里。", "reference_answer": "追踪 Prompt 版本有助于复现、比较和定位变化原因。", "category": "Prompt", "difficulty": "easy", "tags": ["版本管理", "Prompt"], "notes": ""},
        {"query": "few-shot 示例的作用是什么？", "context": "few-shot 示例通过展示目标回答方式，帮助模型更稳定地遵循输出风格和回答模式。", "reference_answer": "few-shot 示例用于引导模型按照期望方式回答。", "category": "Prompt", "difficulty": "easy", "tags": ["few-shot", "Prompt"], "notes": ""},
        {"query": "system prompt 的作用是什么？", "context": "system prompt 用来定义模型的高层行为、约束条件和角色设定。", "reference_answer": "system prompt 用于设定模型的高层行为和约束。", "category": "Prompt", "difficulty": "easy", "tags": ["system prompt", "Prompt"], "notes": ""},
        {"query": "为什么要把 system prompt 和 user prompt 分开？", "context": "把 system prompt 和 user prompt 分开可以保证稳定约束与问题变量分层管理，减少指令冲突。", "reference_answer": "分开设计 system prompt 和 user prompt 有助于保持约束稳定并隔离变量。", "category": "Prompt", "difficulty": "medium", "tags": ["Prompt 架构", "Prompt"], "notes": ""},
        {"query": "temperature 的作用是什么？", "context": "temperature 控制采样随机性。值越低，输出越稳定；值越高，输出越发散。", "reference_answer": "temperature 用于控制模型输出的随机性。", "category": "生成", "difficulty": "easy", "tags": ["temperature", "采样"], "notes": ""},
        {"query": "为什么要做批量实验而不是单条测试？", "context": "批量实验可以观察 Prompt 或模型在不同类别、难度和失败模式上的整体表现，而不是只看个别样本。", "reference_answer": "批量实验有助于从整体上评估方案效果，而不是依赖单个样本。", "category": "实验", "difficulty": "easy", "tags": ["批量实验", "工作流"], "notes": ""},
        {"query": "当上下文不足时，Search QA 应该怎么回答？", "context": "当上下文不足时，系统应该明确说明证据不足，而不是编造看似合理的答案。", "reference_answer": "上下文不足时应明确说明证据不够，避免幻觉。", "category": "策略", "difficulty": "easy", "tags": ["安全", "grounding"], "notes": ""},
        {"query": "为什么评测集中要有 category 元数据？", "context": "category 元数据可以让团队按问题类型切分结果，发现某些类别上的系统性薄弱点。", "reference_answer": "category 元数据有助于分类型分析结果表现。", "category": "数据集", "difficulty": "easy", "tags": ["元数据", "数据集"], "notes": ""},
        {"query": "为什么评测集需要 difficulty 标签？", "context": "difficulty 标签可以帮助团队判断模型在简单、中等和困难问题上的表现差异。", "reference_answer": "difficulty 标签有助于分析模型在不同难度上的表现。", "category": "数据集", "difficulty": "easy", "tags": ["难度", "数据集"], "notes": ""},
        {"query": "什么是 Prompt regression？", "context": "Prompt regression 指新的 Prompt 版本虽然在部分样本上提升了效果，但在另一些样本上出现了回退。", "reference_answer": "Prompt regression 指新版本 Prompt 对部分样本产生了性能回退。", "category": "Prompt", "difficulty": "medium", "tags": ["回归", "Prompt"], "notes": ""},
        {"query": "SQL 为什么在评测工作流里重要？", "context": "SQL 可以帮助团队聚合指标、比较版本、分析失败率，并沉淀可复用的分析模板。", "reference_answer": "SQL 适合用于聚合评测指标和做版本对比分析。", "category": "分析", "difficulty": "easy", "tags": ["SQL", "分析"], "notes": ""},
        {"query": "为什么要记录每条样本的模型输出？", "context": "记录每条样本的模型输出可以支持追溯、人工复查和更细粒度的错误分析。", "reference_answer": "记录模型输出有助于追踪、复盘和细粒度分析。", "category": "平台", "difficulty": "easy", "tags": ["日志", "可追溯"], "notes": ""},
        {"query": "什么是模型评审器？", "context": "模型评审器是用来评估另一个模型输出质量的模型或规则模块，可以评估正确性、完整性和 groundedness 等维度。", "reference_answer": "模型评审器是用于评估模型输出质量的评测模块。", "category": "评测", "difficulty": "medium", "tags": ["LLM judge", "评测"], "notes": ""},
        {"query": "为什么要结合启发式评测和 LLM judge？", "context": "启发式评测成本低且稳定，LLM judge 能补充更语义化的判断，两者结合更平衡。", "reference_answer": "结合启发式评测和 LLM judge 可以兼顾稳定性、成本和语义判断能力。", "category": "评测", "difficulty": "medium", "tags": ["judge", "启发式"], "notes": ""},
        {"query": "notes 字段在数据集管理里有什么价值？", "context": "notes 字段可以记录标注原因、边界情况和后续清洗建议，帮助团队保留样本背景信息。", "reference_answer": "notes 字段可以保存标注背景和后续处理建议。", "category": "数据集", "difficulty": "easy", "tags": ["标注", "运营"], "notes": ""},
        {"query": "数据平台为什么需要 Dashboard？", "context": "Dashboard 可以帮助团队快速查看实验表现、识别风险和进行版本复盘。", "reference_answer": "Dashboard 用于汇总实验表现并支持快速复盘。", "category": "平台", "difficulty": "easy", "tags": ["Dashboard", "分析"], "notes": ""},
        {"query": "为什么要重点看低分样本？", "context": "低分样本通常代表系统最明显的问题，优先分析这些样本有助于更快定位风险。", "reference_answer": "优先分析低分样本有助于更快定位系统问题。", "category": "分析", "difficulty": "easy", "tags": ["优先级", "分析"], "notes": ""},
        {"query": "为什么陈旧上下文会影响 Search QA？", "context": "如果上下文已经过时，模型即使 grounded 也可能给出过期但看似可信的答案。", "reference_answer": "陈旧上下文会让模型基于过期证据生成不再准确的回答。", "category": "检索", "difficulty": "medium", "tags": ["时效性", "Search"], "notes": ""},
        {"query": "元数据过滤为什么能提升检索质量？", "context": "元数据过滤可以在排序前先缩小候选文档范围，例如按时间、来源或领域过滤，从而减少噪音。", "reference_answer": "元数据过滤通过先缩小候选范围来提升检索相关性。", "category": "检索", "difficulty": "medium", "tags": ["元数据过滤", "检索"], "notes": ""},
    ]


def get_demo_prompts() -> List[Dict]:
    return [
        {
            "name": "中文搜索问答基线",
            "description": "偏简洁、强调基于上下文作答的基础 Prompt。",
            "task_type": "search_qa",
            "owner": "open_source",
            "versions": [
                {
                    "version": "v1",
                    "system_prompt": "你是一个搜索问答助手，只能依据提供的上下文回答，不要补充没有证据的信息。",
                    "user_prompt_template": (
                        "问题：{query}\n"
                        "上下文：{context}\n"
                        "类别：{category}\n"
                        "难度：{difficulty}\n\n"
                        "请给出简洁、准确、基于上下文的回答。"
                    ),
                    "few_shot_examples": [
                        {
                            "query": "什么是检索增强生成？",
                            "context": "检索增强生成会先检索外部知识，再基于证据生成回答。",
                            "answer": "检索增强生成是先检索证据，再基于证据生成回答的方法。",
                        }
                    ],
                    "variables_schema": {"query": "str", "context": "str"},
                    "change_note": "基础版本，强调简洁和 grounded 回答。",
                    "is_active": True,
                }
            ],
        },
        {
            "name": "中文搜索问答结构化",
            "description": "要求输出要点并附带证据说明的 Prompt。",
            "task_type": "search_qa",
            "owner": "open_source",
            "versions": [
                {
                    "version": "v1",
                    "system_prompt": "你是一个谨慎的搜索问答助手。如果证据不足，请明确说明不确定。",
                    "user_prompt_template": (
                        "问题：{query}\n"
                        "上下文：{context}\n"
                        "类别：{category}\n"
                        "难度：{difficulty}\n\n"
                        "请使用要点格式回答，并补充一句证据说明。"
                    ),
                    "few_shot_examples": [
                        {
                            "query": "为什么切分粒度会影响检索效果？",
                            "context": "切分粒度会影响召回颗粒度和上下文完整性。",
                            "answer": "- 回答：切分粒度会影响召回精度和上下文完整性。\n- 证据：上下文中明确指出切分粒度会影响召回颗粒度和上下文完整性。",
                        }
                    ],
                    "variables_schema": {"query": "str", "context": "str"},
                    "change_note": "增加结构化输出和证据说明。",
                    "is_active": True,
                }
            ],
        },
        {
            "name": "中文搜索问答JSON",
            "description": "用于测试格式遵循能力的 JSON 输出 Prompt。",
            "task_type": "search_qa",
            "owner": "open_source",
            "versions": [
                {
                    "version": "v1",
                    "system_prompt": "你是一个搜索问答助手，输出必须是合法 JSON。",
                    "user_prompt_template": (
                        "问题：{query}\n"
                        "上下文：{context}\n"
                        "类别：{category}\n"
                        "难度：{difficulty}\n\n"
                        "请返回 JSON，字段为 answer 和 evidence。如果上下文不足，请在 answer 中直接说明。"
                    ),
                    "few_shot_examples": [
                        {
                            "query": "什么是 groundedness？",
                            "context": "groundedness 用于判断回答是否被上下文支持。",
                            "answer": "{\"answer\": \"groundedness 指回答是否被上下文支持。\", \"evidence\": \"上下文说明它用于判断回答是否被上下文支持。\"}",
                        }
                    ],
                    "variables_schema": {"query": "str", "context": "str"},
                    "change_note": "主要用于测试格式遵循能力。",
                    "is_active": True,
                }
            ],
        },
    ]
