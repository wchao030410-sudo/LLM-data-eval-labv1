from datetime import datetime
from html import escape
from typing import Dict, List


def _section_title(text: str, level: int = 2) -> str:
    return "{marks} {text}".format(marks="#" * level, text=text)


def render_markdown_report(report: Dict) -> str:
    lines: List[str] = []
    lines.append("# Prompt 版本对比报告")
    lines.append("")
    lines.append("生成时间：{time}".format(time=report["generated_at"]))
    lines.append("")

    lines.append(_section_title("一、基本信息"))
    lines.append("")
    lines.append("- 数据集：{name}".format(name=report["dataset_name"]))
    lines.append("- 对比对象 A：{name} / {version}".format(**report["version_a"]))
    lines.append("- 对比对象 B：{name} / {version}".format(**report["version_b"]))
    lines.append("- Run A：{run_name}（ID={run_id}）".format(**report["run_a"]))
    lines.append("- Run B：{run_name}（ID={run_id}）".format(**report["run_b"]))
    lines.append("")

    lines.append(_section_title("二、样本量"))
    lines.append("")
    lines.append("- A 样本量：{count}".format(count=report["sample_count_a"]))
    lines.append("- B 样本量：{count}".format(count=report["sample_count_b"]))
    lines.append("- 可直接对比样本量：{count}".format(count=report["paired_sample_count"]))
    lines.append("")

    lines.append(_section_title("三、平均分对比"))
    lines.append("")
    lines.append("| 指标 | A | B | 差值(B-A) |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in report["metric_rows"]:
        lines.append(
            "| {label} | {a:.4f} | {b:.4f} | {diff:+.4f} |".format(
                label=row["label"], a=row["a"], b=row["b"], diff=row["diff"]
            )
        )
    lines.append("")

    lines.append(_section_title("四、Bad Case 分布变化"))
    lines.append("")
    lines.append("| 标签 | A 数量 | B 数量 | 变化(B-A) |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in report["badcase_rows"]:
        lines.append(
            "| {tag} | {a} | {b} | {diff:+d} |".format(
                tag=row["tag"], a=row["a"], b=row["b"], diff=row["diff"]
            )
        )
    lines.append("")

    lines.append(_section_title("五、category 变化"))
    lines.append("")
    lines.append("- 提升最明显：{category}（{delta:+.4f}）".format(**report["top_improved_category"]))
    lines.append("- 下降最明显：{category}（{delta:+.4f}）".format(**report["top_declined_category"]))
    lines.append("")
    lines.append("| category | A 平均分 | B 平均分 | 差值(B-A) |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in report["category_rows"]:
        lines.append(
            "| {category} | {a:.4f} | {b:.4f} | {delta:+.4f} |".format(
                category=row["category"], a=row["a"], b=row["b"], delta=row["delta"]
            )
        )
    lines.append("")

    lines.append(_section_title("六、典型案例对比"))
    lines.append("")
    for idx, case in enumerate(report["case_rows"], start=1):
        lines.append("### 案例 {idx}".format(idx=idx))
        lines.append("")
        lines.append("- 问题：{query}".format(query=case["query"]))
        lines.append("- category：{category}".format(category=case["category"]))
        lines.append("- A 分数：{a_score:.4f}".format(**case))
        lines.append("- B 分数：{b_score:.4f}".format(**case))
        lines.append("- 差值(B-A)：{delta:+.4f}".format(**case))
        lines.append("- A 输出：{a_answer}".format(**case))
        lines.append("- B 输出：{b_answer}".format(**case))
        lines.append("- 参考答案：{reference_answer}".format(**case))
        lines.append("")

    lines.append(_section_title("七、结论与建议"))
    lines.append("")
    for item in report["conclusions"]:
        lines.append("- {item}".format(item=item))
    lines.append("")
    return "\n".join(lines)


def render_html_report(report: Dict) -> str:
    def table(headers: List[str], rows: List[List[str]]) -> str:
        header_html = "".join("<th>{}</th>".format(escape(item)) for item in headers)
        row_html = ""
        for row in rows:
            row_html += "<tr>{}</tr>".format("".join("<td>{}</td>".format(escape(str(cell))) for cell in row))
        return "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(header_html, row_html)

    metric_table = table(
        ["指标", "A", "B", "差值(B-A)"],
        [[item["label"], f'{item["a"]:.4f}', f'{item["b"]:.4f}', f'{item["diff"]:+.4f}'] for item in report["metric_rows"]],
    )
    badcase_table = table(
        ["标签", "A 数量", "B 数量", "变化(B-A)"],
        [[item["tag"], item["a"], item["b"], f'{item["diff"]:+d}'] for item in report["badcase_rows"]],
    )
    category_table = table(
        ["category", "A 平均分", "B 平均分", "差值(B-A)"],
        [[item["category"], f'{item["a"]:.4f}', f'{item["b"]:.4f}', f'{item["delta"]:+.4f}'] for item in report["category_rows"]],
    )
    case_html = ""
    for idx, case in enumerate(report["case_rows"], start=1):
        case_html += """
        <section class="case">
          <h3>案例 {idx}</h3>
          <p><strong>问题：</strong>{query}</p>
          <p><strong>category：</strong>{category}</p>
          <p><strong>A 分数：</strong>{a_score:.4f} &nbsp; <strong>B 分数：</strong>{b_score:.4f} &nbsp; <strong>差值：</strong>{delta:+.4f}</p>
          <p><strong>A 输出：</strong>{a_answer}</p>
          <p><strong>B 输出：</strong>{b_answer}</p>
          <p><strong>参考答案：</strong>{reference_answer}</p>
        </section>
        """.format(
            idx=idx,
            query=escape(case["query"]),
            category=escape(case["category"]),
            a_score=case["a_score"],
            b_score=case["b_score"],
            delta=case["delta"],
            a_answer=escape(case["a_answer"]),
            b_answer=escape(case["b_answer"]),
            reference_answer=escape(case["reference_answer"]),
        )

    conclusions = "".join("<li>{}</li>".format(escape(item)) for item in report["conclusions"])

    return """
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Prompt 版本对比报告</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans SC", sans-serif; background: #f6f8fb; color: #102033; margin: 0; }}
        .wrap {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 64px; }}
        .hero {{ background: linear-gradient(135deg, #0f172a, #1d4ed8); color: #fff; padding: 24px 28px; border-radius: 20px; }}
        .panel {{ background: #fff; border: 1px solid rgba(16,32,51,0.08); border-radius: 18px; padding: 20px 22px; margin-top: 18px; box-shadow: 0 10px 24px rgba(15,23,42,0.06); }}
        h1, h2, h3 {{ margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
        th {{ background: #f8fafc; }}
        .case p {{ line-height: 1.7; }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="hero">
          <h1>Prompt 版本对比报告</h1>
          <p>生成时间：{generated_at}</p>
        </div>
        <div class="panel">
          <h2>基本信息</h2>
          <p><strong>数据集：</strong>{dataset_name}</p>
          <p><strong>对比对象 A：</strong>{a_name} / {a_version}</p>
          <p><strong>对比对象 B：</strong>{b_name} / {b_version}</p>
          <p><strong>Run A：</strong>{run_a_name}（ID={run_a_id}）</p>
          <p><strong>Run B：</strong>{run_b_name}（ID={run_b_id}）</p>
        </div>
        <div class="panel">
          <h2>样本量</h2>
          <p>A 样本量：{sample_a}</p>
          <p>B 样本量：{sample_b}</p>
          <p>可直接对比样本量：{paired}</p>
        </div>
        <div class="panel">
          <h2>平均分对比</h2>
          {metric_table}
        </div>
        <div class="panel">
          <h2>Bad Case 分布变化</h2>
          {badcase_table}
        </div>
        <div class="panel">
          <h2>category 变化</h2>
          <p><strong>提升最明显：</strong>{best_category}（{best_delta:+.4f}）</p>
          <p><strong>下降最明显：</strong>{worst_category}（{worst_delta:+.4f}）</p>
          {category_table}
        </div>
        <div class="panel">
          <h2>典型案例对比</h2>
          {case_html}
        </div>
        <div class="panel">
          <h2>结论与建议</h2>
          <ul>{conclusions}</ul>
        </div>
      </div>
    </body>
    </html>
    """.format(
        generated_at=escape(report["generated_at"]),
        dataset_name=escape(report["dataset_name"]),
        a_name=escape(report["version_a"]["name"]),
        a_version=escape(report["version_a"]["version"]),
        b_name=escape(report["version_b"]["name"]),
        b_version=escape(report["version_b"]["version"]),
        run_a_name=escape(report["run_a"]["run_name"]),
        run_a_id=report["run_a"]["run_id"],
        run_b_name=escape(report["run_b"]["run_name"]),
        run_b_id=report["run_b"]["run_id"],
        sample_a=report["sample_count_a"],
        sample_b=report["sample_count_b"],
        paired=report["paired_sample_count"],
        metric_table=metric_table,
        badcase_table=badcase_table,
        best_category=escape(report["top_improved_category"]["category"]),
        best_delta=report["top_improved_category"]["delta"],
        worst_category=escape(report["top_declined_category"]["category"]),
        worst_delta=report["top_declined_category"]["delta"],
        category_table=category_table,
        case_html=case_html,
        conclusions=conclusions,
    )


def build_report_filename(version_a: Dict, version_b: Dict, fmt: str) -> str:
    suffix = "md" if fmt == "markdown" else "html"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return "prompt_compare_{a}_{av}_vs_{b}_{bv}_{ts}.{suffix}".format(
        a=version_a["name"].replace(" ", "_"),
        av=version_a["version"],
        b=version_b["name"].replace(" ", "_"),
        bv=version_b["version"],
        ts=timestamp,
        suffix=suffix,
    )
