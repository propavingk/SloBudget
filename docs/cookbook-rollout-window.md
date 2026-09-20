# Cookbook: auditing a rollout window

After an incident, the first question is usually how much budget the incident
spent and whether the paging alert should have fired. This is the routine.

## 1. Keep one SLI file per service per window

```
samples/service-a.sli
```

The format is one interval per line: timestamp, good events, total events.
Comments with `#` are allowed.

## 2. Read the budget before the incident window

```
python -m slobudget burn service-a.sli --objective 99.9 --window 30d --as-of 2026-03-01T00:00:00Z
```

The report prints the budget, what the observed failures spent, and the burn
rate over each window. The `--as-of` flag keeps two audits comparable by
fixing the evaluation instant.

## 3. Check the alerts the same way

```
python -m slobudget alerts service-a.sli --objective 99.9 --window 30d
```

The alert evaluation prints which threshold would have fired and at which
timestamp. A page that fired with no alert line, or the reverse, is the
finding worth a ticket.

## 4. Attach the report to the postmortem

The output is deterministic, so attach it as-is and link the SLI file
revision. Two identical runs prove the numbers were not retyped.
