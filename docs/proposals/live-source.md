# Proposal: a live metrics source

Status: closed, not planned for this tool.

The idea is to read samples from a live metrics backend instead of a file,
removing the export step.

Out of scope by design: the output would stop being reproducible from the
files committed next to the postmortem, and the tool would need credentials,
network error handling, and a story for exactly which samples a past audit
saw. Exporting a window to an SLI file and running the existing arithmetic
is a few seconds of work and keeps every audit answerable from its inputs.
