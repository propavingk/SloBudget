# FAQ

**What is the difference between `burn` and `alerts`?**
`burn` reports the budget and the burn rate windows. `alerts` evaluates the
fast burn and slow burn thresholds and says which one would have fired.

**Why does the burn rate read null sometimes?**
A window with fewer than two samples cannot produce a rate. The tool reports
null instead of guessing, and the text report says insufficient data.

**Does it store state between runs?**
No. Every run reads the SLI file and prints a report. Determinism is a
feature: the same input bytes produce byte identical output.

**Can I point it at a live metrics system?**
No. The tool reads files, which is why a postmortem can reproduce an audit
months later from the same input.
