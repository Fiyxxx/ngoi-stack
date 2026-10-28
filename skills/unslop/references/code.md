# Code slop

- Comments that narrate what the code does, restate a name, mark sections with banners, describe the change ("now uses X"), or justify a workaround. Keep only a non-obvious why, license headers, and docs for a public API.
- Commented-out code, dead code, and unused exports, imports, parameters or variables.
- Wrappers and helpers with one caller. Abstractions with one implementation. Options, flags or config nobody sets.
- Guards for states that can't happen. Re-validating data that internal types already guarantee.
- Defaults that hide bugs (`?? []`, `or {}`, `|| ''`) where the value can never be missing.
- `try`/`except` or `catch` that only logs and carries on, and broad catches that swallow errors.
- Logic duplicated from existing code. Use the existing code.
- Generic names (`data`, `result`, `info`, `handle`, `manager`, `utils`, `helper`) where a domain name exists.
- Functions split for no reason, or one long function doing several jobs.
- Casts and suppressions (`as any`, `as unknown as`, `# type: ignore`) used instead of fixing the type.
- Debug prints and leftover logging.
- Tests that assert implementation details instead of behaviour a caller can observe.
