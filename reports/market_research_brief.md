# Market Research Brief — Employee Attrition Benchmarks

Short context for interpreting this portfolio analysis. Figures below are widely cited industry ranges, not claims about any specific employer.

## Industry context (high level)

| Topic | Commonly cited range | Relevance to this project |
|-------|----------------------|---------------------------|
| Voluntary turnover | Often mid-teens % annually in U.S. private sector (varies widely by industry and year; BLS JOLTS / SHRM surveys) | This dataset’s overall attrition is **16.1%**, in a plausible “elevated but not extreme” band for an illustrative HR sample |
| Cost of turnover | Frequently **50%–200% of annual salary**, depending on role seniority and how fully loaded costs are counted (recruiting, onboarding, productivity loss) | Excel model uses **150%** of annual salary — a mid professional / knowledge-worker assumption within that range |
| Time-to-fill | Often **30–60+ days** depending on role and market (SHRM / LinkedIn talent reports) | Supports treating each prevented exit as material operational cost, not only a line-item hire fee |
| Common drivers | Compensation, burnout/workload, career growth, manager quality | Analysis finds **overtime** as the top statistical driver here, consistent with workload/burnout themes in industry reporting |

## Comparison to dataset findings

| Benchmark theme | What this analysis shows |
|-----------------|--------------------------|
| Overall turnover level | **16.1%** attrition (237 / 1,470) |
| Workload / burnout | Overtime Yes **30.5%** vs No **10.4%**; OverTime ranks #1 in both models |
| Early tenure risk | **0–2 years** tenure band at **34.9%** attrition |
| Pay | Lowest income quartile **29.4%** attrition vs ~10% in the top quartile |
| Intervention ROI framing | Flagging **31** high-risk current employees projects **~$455k** savings at 42% effectiveness and 150% replacement cost |

**Takeaway for stakeholders:** The headline risk pattern (overtime / workload) aligns with common external narratives; the dollar figure is an **illustrative** model on public sample data, not a forecast for a live employer.

## Sources (starting points)

- U.S. Bureau of Labor Statistics — [Job Openings and Labor Turnover Survey (JOLTS)](https://www.bls.gov/jlt/)
- SHRM — resources on [turnover cost and retention](https://www.shrm.org/) (member/survey publications; ranges vary by year)
- Project cost assumptions documented in `reports/cost_of_turnover.xlsx` (Assumptions sheet comments)
