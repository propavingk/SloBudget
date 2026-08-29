
## Reading the gap sample

`service-b-gap.sli` has a deliberate hole: no samples between 02:00 and 03:00.
The gap is data, not an error. The report counts the gap, keeps the window
arithmetic honest across it, and never treats a missing interval as a healthy
one. Compare its burndown with `service-a.sli` to see the difference.
