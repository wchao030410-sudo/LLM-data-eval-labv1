MANUAL_REVIEW_QUEUE_SQL = """
SELECT
  er.id AS evaluation_result_id,
  run.run_name,
  s.category,
  s.difficulty,
  json_extract(er.judge_detail, '$.benchmark_profile.display_name') AS benchmark_profile,
  json_extract(er.judge_detail, '$.manual_review.priority') AS review_priority,
  json_extract(er.judge_detail, '$.manual_review.review_queue') AS review_queue,
  er.overall_score,
  er.hallucination_risk
FROM evaluation_results er
JOIN experiment_runs run ON run.id = er.experiment_run_id
JOIN samples s ON s.id = er.sample_id
WHERE json_extract(er.judge_detail, '$.manual_review.required') = 1
ORDER BY
  CASE json_extract(er.judge_detail, '$.manual_review.priority')
    WHEN 'p0' THEN 0
    WHEN 'p1' THEN 1
    WHEN 'p2' THEN 2
    ELSE 3
  END,
  er.overall_score ASC;
""".strip()


BENCHMARK_SLICE_SQL = """
SELECT
  json_extract(er.judge_detail, '$.benchmark_profile.profile_name') AS benchmark_profile,
  s.category,
  COUNT(*) AS sample_count,
  ROUND(AVG(er.overall_score), 4) AS avg_overall_score,
  ROUND(AVG(json_extract(er.judge_detail, '$.business_scorecard.benchmark_score')), 4) AS avg_benchmark_score,
  ROUND(AVG(json_extract(er.judge_detail, '$.business_scorecard.user_trust_score')), 4) AS avg_user_trust_score
FROM evaluation_results er
JOIN samples s ON s.id = er.sample_id
GROUP BY 1, 2
ORDER BY avg_benchmark_score DESC;
""".strip()


DATA_PRODUCTION_PRIORITY_SQL = """
SELECT
  er.id AS evaluation_result_id,
  s.id AS sample_id,
  s.category,
  s.difficulty,
  json_extract(er.judge_detail, '$.data_production.training_priority') AS training_priority,
  json_extract(er.judge_detail, '$.data_production.annotation_complexity') AS annotation_complexity,
  json_extract(er.judge_detail, '$.data_production.qa_sampling_ratio') AS qa_sampling_ratio,
  er.overall_score,
  er.correctness,
  er.groundedness
FROM evaluation_results er
JOIN samples s ON s.id = er.sample_id
WHERE json_extract(er.judge_detail, '$.data_production.training_priority') IN ('p0', 'p1')
ORDER BY
  CASE json_extract(er.judge_detail, '$.data_production.training_priority')
    WHEN 'p0' THEN 0
    ELSE 1
  END,
  er.overall_score ASC;
""".strip()
