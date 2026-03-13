-- LLM Data Eval Lab 分析 SQL 示例
-- 说明：
-- 1. 下面 SQL 基于当前项目的 SQLite 表结构
-- 2. 这些查询主要用于展示 Prompt 对比、失败率、幻觉率、差例分析与趋势复盘能力


-- 1. 不同 Prompt 版本的平均总分
-- 用于比较 Prompt 版本的整体离线效果
SELECT
    p.name AS prompt_name,
    pv.version AS prompt_version,
    ROUND(AVG(er.overall_score), 4) AS avg_overall_score,
    COUNT(*) AS sample_count
FROM evaluation_results er
JOIN experiment_runs r ON r.id = er.experiment_run_id
JOIN experiments e ON e.id = r.experiment_id
JOIN prompt_versions pv ON pv.id = e.prompt_version_id
JOIN prompts p ON p.id = pv.prompt_id
GROUP BY p.name, pv.version
ORDER BY avg_overall_score DESC, sample_count DESC;


-- 2. 各类问题的失败率
-- 失败定义：overall_score < 0.60
SELECT
    s.category,
    COUNT(*) AS total_samples,
    SUM(CASE WHEN er.overall_score < 0.60 THEN 1 ELSE 0 END) AS failed_samples,
    ROUND(1.0 * SUM(CASE WHEN er.overall_score < 0.60 THEN 1 ELSE 0 END) / COUNT(*), 4) AS failure_rate
FROM evaluation_results er
JOIN samples s ON s.id = er.sample_id
GROUP BY s.category
ORDER BY failure_rate DESC, total_samples DESC;


-- 3. 幻觉率统计
-- 统计各 Prompt 版本的平均 hallucination_risk
SELECT
    p.name AS prompt_name,
    pv.version AS prompt_version,
    ROUND(AVG(er.hallucination_risk), 4) AS avg_hallucination_risk,
    ROUND(AVG(CASE WHEN er.hallucination_risk >= 0.50 THEN 1.0 ELSE 0.0 END), 4) AS hallucination_case_ratio
FROM evaluation_results er
JOIN experiment_runs r ON r.id = er.experiment_run_id
JOIN experiments e ON e.id = r.experiment_id
JOIN prompt_versions pv ON pv.id = e.prompt_version_id
JOIN prompts p ON p.id = pv.prompt_id
GROUP BY p.name, pv.version
ORDER BY avg_hallucination_risk DESC;


-- 4. 最近实验趋势
-- 查看最近 10 次运行的平均总分变化
SELECT
    r.id AS run_id,
    r.run_name,
    r.created_at,
    ROUND(AVG(er.overall_score), 4) AS avg_overall_score,
    ROUND(AVG(er.hallucination_risk), 4) AS avg_hallucination_risk
FROM experiment_runs r
JOIN evaluation_results er ON er.experiment_run_id = r.id
GROUP BY r.id, r.run_name, r.created_at
ORDER BY r.created_at DESC
LIMIT 10;


-- 5. 格式错误统计
-- 查看哪些 Prompt 版本更容易出现格式不符合要求的问题
SELECT
    p.name AS prompt_name,
    pv.version AS prompt_version,
    COUNT(*) AS total_results,
    SUM(CASE WHEN er.format_compliance < 0.60 THEN 1 ELSE 0 END) AS format_error_count,
    ROUND(1.0 * SUM(CASE WHEN er.format_compliance < 0.60 THEN 1 ELSE 0 END) / COUNT(*), 4) AS format_error_ratio
FROM evaluation_results er
JOIN experiment_runs r ON r.id = er.experiment_run_id
JOIN experiments e ON e.id = r.experiment_id
JOIN prompt_versions pv ON pv.id = e.prompt_version_id
JOIN prompts p ON p.id = pv.prompt_id
GROUP BY p.name, pv.version
ORDER BY format_error_ratio DESC, format_error_count DESC;


-- 6. 低分样本排行
-- 找出最值得人工复盘的低分样本
SELECT
    er.id AS evaluation_result_id,
    r.run_name,
    s.id AS sample_id,
    s.query,
    s.category,
    s.difficulty,
    ROUND(er.overall_score, 4) AS overall_score,
    ROUND(er.hallucination_risk, 4) AS hallucination_risk
FROM evaluation_results er
JOIN experiment_runs r ON r.id = er.experiment_run_id
JOIN samples s ON s.id = er.sample_id
ORDER BY er.overall_score ASC, er.hallucination_risk DESC
LIMIT 20;


-- 7. 不同 difficulty 的表现
-- 查看 easy / medium / hard 的平均表现差异
SELECT
    s.difficulty,
    COUNT(*) AS total_results,
    ROUND(AVG(er.correctness), 4) AS avg_correctness,
    ROUND(AVG(er.completeness), 4) AS avg_completeness,
    ROUND(AVG(er.groundedness), 4) AS avg_groundedness,
    ROUND(AVG(er.overall_score), 4) AS avg_overall_score
FROM evaluation_results er
JOIN samples s ON s.id = er.sample_id
GROUP BY s.difficulty
ORDER BY avg_overall_score DESC;


-- 8. 各 Bad Case 标签占比
-- 统计不同 failure mode 在全部差例中的占比
SELECT
    bt.code AS badcase_tag,
    COUNT(*) AS hit_count,
    ROUND(
        1.0 * COUNT(*) /
        (SELECT COUNT(*) FROM evaluation_result_badcase_tags),
        4
    ) AS tag_ratio
FROM evaluation_result_badcase_tags link
JOIN badcase_tags bt ON bt.id = link.badcase_tag_id
GROUP BY bt.code
ORDER BY hit_count DESC;


-- 9. 各 category 在 groundedness 上的表现
-- 看哪些类型更容易出现 grounding 问题
SELECT
    s.category,
    ROUND(AVG(er.groundedness), 4) AS avg_groundedness,
    ROUND(AVG(er.hallucination_risk), 4) AS avg_hallucination_risk,
    COUNT(*) AS total_results
FROM evaluation_results er
JOIN samples s ON s.id = er.sample_id
GROUP BY s.category
ORDER BY avg_groundedness ASC, avg_hallucination_risk DESC;


-- 10. 单次运行的评分分布
-- 用于分析某个 run 内部是否存在明显长尾失败
-- 使用前可将 :run_id 替换成实际 run id
SELECT
    er.experiment_run_id,
    CASE
        WHEN er.overall_score < 0.40 THEN '[0.0, 0.4)'
        WHEN er.overall_score < 0.60 THEN '[0.4, 0.6)'
        WHEN er.overall_score < 0.80 THEN '[0.6, 0.8)'
        ELSE '[0.8, 1.0]'
    END AS score_bucket,
    COUNT(*) AS sample_count
FROM evaluation_results er
WHERE er.experiment_run_id = :run_id
GROUP BY er.experiment_run_id, score_bucket
ORDER BY score_bucket;
