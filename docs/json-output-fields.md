# JSON output fields

Both `burn` and `alerts` accept `--json` and print one object per run.

| Field | Type | Meaning |
|---|---|---|
| service | string | Service name read from the file header |
| objective | number | The declared objective, for example 0.999 |
| window | string | Compliance window, for example 30d |
| as_of | string | Evaluation instant, UTC, ISO 8601 |
| budget | integer | Error budget in events |
| consumed | integer | Bad events inside the compliance window |
| consumed_ratio | number | Consumed divided by budget |
| burn_1h | number or null | Failure ratio over the one hour window divided by the tolerated ratio |
| burn_6h | number or null | Same over six hours |
| alert | string or null | The threshold that would have fired, when one does |
| projection_days | number or null | Days until budget exhaustion at the current rate, when the rate is above one |

Null means the data did not support an answer. A window with fewer than two
samples reports null rather than guessing.
