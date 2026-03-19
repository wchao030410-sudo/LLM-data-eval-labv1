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
          <div class="case-head">
            <h3>案例 {idx}</h3>
            <div class="case-scores">
              <span>A {a_score:.4f}</span>
              <span>B {b_score:.4f}</span>
              <span>{delta:+.4f}</span>
            </div>
          </div>
          <p class="case-query"><strong>问题：</strong>{query}</p>
          <p class="case-meta"><strong>category：</strong>{category}</p>
          <div class="case-block"><strong>A 输出：</strong><div>{a_answer}</div></div>
          <div class="case-block"><strong>B 输出：</strong><div>{b_answer}</div></div>
          <div class="case-block"><strong>参考答案：</strong><div>{reference_answer}</div></div>
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
        :root {{
          --bg-0: #04101d;
          --bg-1: #0c1f39;
          --panel: rgba(9, 18, 31, 0.92);
          --panel-soft: rgba(13, 24, 40, 0.88);
          --line: rgba(140, 179, 255, 0.16);
          --ink: #eef6ff;
          --ink-soft: #a6c1df;
          --cyan: #72e3ff;
          --cobalt: #5f7cff;
          --emerald: #62f2c2;
          --amber: #ffc977;
          --rose: #ff7ea7;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          font-family: "Noto Sans SC", "PingFang SC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: var(--ink);
          background:
            radial-gradient(circle at 14% 0%, rgba(95, 124, 255, 0.16), transparent 24%),
            radial-gradient(circle at 88% 18%, rgba(114, 227, 255, 0.14), transparent 20%),
            linear-gradient(180deg, var(--bg-0) 0%, #071527 36%, var(--bg-1) 100%);
        }}
        .wrap {{
          max-width: 1120px;
          margin: 0 auto;
          padding: 32px 20px 72px;
        }}
        .hero {{
          position: relative;
          overflow: hidden;
          padding: 28px 30px;
          border-radius: 28px;
          border: 1px solid var(--line);
          background:
            radial-gradient(circle at 84% 16%, rgba(114, 227, 255, 0.24), transparent 18%),
            linear-gradient(135deg, rgba(4, 10, 18, 0.96) 0%, rgba(8, 24, 44, 0.94) 42%, rgba(17, 41, 74, 0.94) 100%);
          box-shadow: 0 24px 64px rgba(0, 6, 18, 0.36);
        }}
        .hero .eyebrow {{
          display: inline-block;
          padding: 6px 12px;
          border-radius: 999px;
          border: 1px solid rgba(114, 227, 255, 0.24);
          background: rgba(8, 19, 33, 0.62);
          color: #9fd8ff;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.16em;
          text-transform: uppercase;
        }}
        .hero h1, .panel h2, .case h3 {{
          margin: 0;
          font-family: "Segoe UI", "Noto Sans SC", sans-serif;
        }}
        .hero h1 {{
          margin-top: 14px;
          font-size: 36px;
          line-height: 1.08;
        }}
        .hero p {{
          margin: 10px 0 0 0;
          color: #d7e7fb;
          line-height: 1.8;
        }}
        .summary-grid {{
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 14px;
          margin-top: 18px;
        }}
        .summary-card {{
          padding: 16px 18px;
          border-radius: 20px;
          border: 1px solid var(--line);
          background: rgba(8, 18, 31, 0.72);
        }}
        .summary-card .label {{
          color: #9ec8f2;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.14em;
          text-transform: uppercase;
        }}
        .summary-card .value {{
          margin-top: 8px;
          font-size: 30px;
          font-weight: 800;
        }}
        .summary-card .desc {{
          margin-top: 6px;
          color: var(--ink-soft);
          line-height: 1.7;
        }}
        .summary-card.cobalt .value {{ color: #b8cbff; }}
        .summary-card.cyan .value {{ color: #9cecff; }}
        .summary-card.emerald .value {{ color: #97ffd7; }}
        .meta-grid {{
          display: grid;
          grid-template-columns: 1.08fr 0.92fr;
          gap: 18px;
        }}
        .panel {{
          margin-top: 18px;
          padding: 22px 24px;
          border-radius: 24px;
          border: 1px solid var(--line);
          background: var(--panel);
          box-shadow: 0 18px 48px rgba(0, 8, 20, 0.24);
        }}
        .panel h2 {{
          margin-bottom: 14px;
          font-size: 24px;
          color: #f5fbff;
        }}
        .panel p, .panel li {{
          color: var(--ink-soft);
          line-height: 1.8;
        }}
        .panel ul {{
          margin: 0;
          padding-left: 18px;
        }}
        .meta-list {{
          display: grid;
          gap: 12px;
        }}
        .meta-item {{
          padding: 14px 16px;
          border-radius: 18px;
          border: 1px solid rgba(140, 179, 255, 0.12);
          background: var(--panel-soft);
        }}
        .meta-item strong {{
          color: #f1f8ff;
        }}
        table {{
          width: 100%;
          border-collapse: separate;
          border-spacing: 0;
          margin-top: 12px;
          overflow: hidden;
          border-radius: 18px;
        }}
        th, td {{
          padding: 12px 14px;
          text-align: left;
        }}
        thead th {{
          background: rgba(11, 22, 37, 0.98);
          color: #f5fbff;
          border-bottom: 1px solid rgba(140, 179, 255, 0.18);
        }}
        tbody td {{
          background: rgba(9, 17, 29, 0.82);
          color: #dbe9fb;
          border-bottom: 1px solid rgba(140, 179, 255, 0.08);
        }}
        .case-grid {{
          display: grid;
          gap: 16px;
        }}
        .case {{
          padding: 18px;
          border-radius: 22px;
          border: 1px solid rgba(140, 179, 255, 0.14);
          background: var(--panel-soft);
        }}
        .case-head {{
          display: flex;
          justify-content: space-between;
          gap: 16px;
          align-items: center;
        }}
        .case-scores {{
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }}
        .case-scores span {{
          padding: 6px 10px;
          border-radius: 999px;
          background: rgba(7, 18, 31, 0.84);
          border: 1px solid rgba(114, 227, 255, 0.16);
          color: #d9ecff;
          font-size: 13px;
        }}
        .case-query {{
          margin-top: 12px;
        }}
        .case-meta {{
          margin-top: 6px;
        }}
        .case-block {{
          margin-top: 12px;
          padding: 12px 14px;
          border-radius: 16px;
          background: rgba(7, 17, 29, 0.72);
          border: 1px solid rgba(140, 179, 255, 0.08);
        }}
        .case-block strong {{
          display: block;
          margin-bottom: 6px;
          color: #f1f8ff;
        }}
        .case-block div {{
          color: var(--ink-soft);
          line-height: 1.8;
          white-space: pre-wrap;
        }}
        @media (max-width: 900px) {{
          .summary-grid,
          .meta-grid {{
            grid-template-columns: 1fr;
          }}
          .case-head {{
            flex-direction: column;
            align-items: flex-start;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="hero">
          <div class="eyebrow">Prompt Comparison Report</div>
          <h1>Prompt 版本对比报告</h1>
          <p>生成时间：{generated_at}</p>
          <div class="summary-grid">
            <div class="summary-card cobalt">
              <div class="label">Paired Samples</div>
              <div class="value">{paired}</div>
              <div class="desc">两个版本都能直接对比的样本量。</div>
            </div>
            <div class="summary-card cyan">
              <div class="label">Top Improved</div>
              <div class="value">{best_category}</div>
              <div class="desc">当前提升最明显的类别。</div>
            </div>
            <div class="summary-card emerald">
              <div class="label">Most Declined</div>
              <div class="value">{worst_category}</div>
              <div class="desc">当前下降最明显的类别。</div>
            </div>
          </div>
        </div>
        <div class="meta-grid">
          <div class="panel">
            <h2>基本信息</h2>
            <div class="meta-list">
              <div class="meta-item"><strong>数据集：</strong>{dataset_name}</div>
              <div class="meta-item"><strong>对比对象 A：</strong>{a_name} / {a_version}</div>
              <div class="meta-item"><strong>对比对象 B：</strong>{b_name} / {b_version}</div>
              <div class="meta-item"><strong>Run A：</strong>{run_a_name}（ID={run_a_id}）</div>
              <div class="meta-item"><strong>Run B：</strong>{run_b_name}（ID={run_b_id}）</div>
            </div>
          </div>
          <div class="panel">
            <h2>样本量</h2>
            <div class="meta-list">
              <div class="meta-item"><strong>A 样本量：</strong>{sample_a}</div>
              <div class="meta-item"><strong>B 样本量：</strong>{sample_b}</div>
              <div class="meta-item"><strong>可直接对比样本量：</strong>{paired}</div>
              <div class="meta-item"><strong>最佳类别：</strong>{best_category}（{best_delta:+.4f}）</div>
            </div>
          </div>
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
          <div class="case-grid">{case_html}</div>
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
