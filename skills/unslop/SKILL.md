---
name: unslop
description: Remove AI slop from code, wording and UI. Used by ngoi build before review. Also use when the user asks to unslop or clean up code, text, copy or a UI.
---

# Unslop

Scope: the diff, or the files the user names. Touch only what the change introduced unless asked.

1. **Search** the changed lines for the textual tells in the lists below.
2. **Read** the change against each list that applies:
   - code: [references/code.md](references/code.md)
   - wording: [references/wording.md](references/wording.md), for UI text, error messages, docs and PR text
   - UI: [references/ui.md](references/ui.md)
3. **Fix in place.** Keep behaviour and meaning. Never touch test assertions. The repo's own design system and conventions win over these lists.

**Report:** what you removed, per list, and anything you left on purpose with the reason.
