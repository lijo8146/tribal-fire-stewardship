# Observation table contract

One row is one predeclared aggregated observation for one sampling unit and one period. The included table contains headers only. Keep records and a completed protocol in `data/private/`, or in another location chosen by the partner.

| Column | Meaning |
|---|---|
| pair_id | Stable identifier for one independently selected treated/comparison pair |
| unit_id | Stable identifier for a sampling unit, unchanged before and after |
| role | `treated` or `comparison` |
| period | `before` or `after` |
| observed_at | ISO date/time describing the agreed observation/aggregate window |
| indicator | One locally selected indicator per analysis |
| value | Finite numeric observation in the declared units |
| unit | Identical unit label throughout one analysis |
| method | Identical method label throughout one analysis |
| quality_flag | `accepted` only after the agreed review rules have been applied |

The helper requires exactly one row in each of the four role/period cells per pair. Aggregate repeat visits using the protocol before constructing this table. Do not reuse a comparison unit across pairs and then bootstrap those pairs as independent. Do not mix treatments, indicators, units or methods in one estimate. A protocol treatment date is checked by the research notebook when provided.

The numeric helper verifies the observation structure; it cannot verify consent, independence, measurement validity or causal identification. Those require the research design and appropriate review.
