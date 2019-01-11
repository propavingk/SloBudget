# Sample fixtures

These files are test vectors, authored by hand for this project. They are not
captured production telemetry. Each row is one interval:

```
<iso8601-utc-timestamp>,<good>,<total>
```

The timestamp marks the interval start. Lines beginning with `#` are comments.

## service-a.sli

A synthetic service level indicator over four hours at five minute intervals,
2000 events per interval, starting at 2026-03-01T00:00:00Z. It was constructed
to exercise the full accounting path:

- 00:00 to 00:55, twelve healthy intervals, one bad event each.
- 01:00 to 01:25, six incident intervals, 220 bad events each (11 percent
  failure), a sharp burn.
- 01:30 to 01:55, six recovery intervals, 30 bad events each, tapering.
- 02:00 to 03:55, twenty four healthy intervals, one bad event each.

Totals: 96000 events, 1536 bad. Against a 98 percent objective the budget is
1920 events, so the run consumes 80 percent and ends with 20.0 percent
remaining. Against a 99.9 percent objective the same incident is a fast burn
that trips the multi window alert.
