# Principles

- Make the smallest change that solves the problem. Delete before adding. No new layers, options or wrappers until something needs them.
- Name the data shape first. Make illegal states unrepresentable.
- Follow the repo's existing patterns before inventing new ones.
- Fix root causes. A guard is a fix only when the state it handles can really happen.
- Validate at system boundaries. Trust internal types.
- Prove it works on the real thing: run it and read the real value. Tests are necessary, not sufficient.
- Never weaken a check to make it pass. No suppressions, skipped tests or loosened config without the user's OK.
- Comments only for a non-obvious why.
- Label claims as verified, inferred or guessed.
- Push back with evidence. "No" is an acceptable answer.
