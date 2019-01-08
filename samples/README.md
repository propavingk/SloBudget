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
