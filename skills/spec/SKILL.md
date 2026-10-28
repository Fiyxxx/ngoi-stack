---
name: spec
description: Turn the user's rough dump into a short, approved spec for work of any size, then start the build on "go". Use when the user types /ngoi:spec.
disable-model-invocation: true
---

# Spec

The user dumps what they want, often rambling. Find what they actually want, settle the decisions that matter with them, and write the shortest spec that lets agents build without guessing and lets a reviewer prove the result. The spec is for agents and for review. It is not a document to admire.

## 1. Ground

Read before you ask. Use Explore subagents for wide reads and keep their summaries, not their dumps. Read earlier specs in `.ngoi/specs/`: don't re-ask decisions they settled, and flag any conflict. If `.ngoi/check` is missing, mention `/ngoi:setup`. The spec works without it, but review needs it.

## 2. Play back and plan, in one message

- **Goal** in your own words: what, who it's for, what's out of scope.
- **Size:** a tweak (a few lines, no design choices), a feature, or big (several PR-sized units).
- **Approach** and the main changes. For big work, list the units in order, one line each. For a new app, the first unit sets up something runnable and `.ngoi/verify.md`. Across repos, the contract between them comes before the code on either side.
- **Done checks.** Each is an observable outcome plus the evidence that will prove it, such as a screen and the stored data, a response, or a log line. Review is bounded by these, so the user must see them now.
- **Decisions.** The open choices that would change the result, each with your recommendation and one line of why. Mark which come from the user and which are your guesses. If running something can settle a question (layout, timing, behaviour, whether an approach works), settle it with a quick throwaway prototype and show the result instead of asking.

Consider several approaches privately and drop the weak ones. Show a comparison only when it helps the user decide. Keep the message readable in two minutes. For a tweak, say what you'll change and how you'll prove it.

## 3. Push back

The user will challenge you. Answer with evidence from the code (file:line), not reassurance. If they're right, change the plan and say what changed. If you still disagree, say so once with the reason, then follow their call. Repeat until they approve.

## 4. Write the spec

Path: `.ngoi/specs/YYYY-MM-DD-<slug>.md`. A tweak gets no file; the chat is its spec.

```
# <title>
Goal: one or two sentences, and who notices.
Not doing:
Constraints:
Decisions: each marked (user) or (agent's call).
Done checks:
- [ ] D1 <observable outcome>. Evidence: <what proves it, how it's produced>
Sketch: types, signatures, data shapes, module boundaries. Code, no bodies.
Review focus: up to 5 inputs or situations most likely to break it.
Units (big work only):
- [ ] U1 <one line> (D1, D3)
Open questions:
Log:
```

- The spec is shorter than the code it describes.
- No function bodies, except an algorithm the signature and checks don't determine, or exact wording the user fixed.
- No step-by-step instructions. Agents read the code.
- Sketch it twice in private: two structurally different shapes. Keep the one with the smaller public surface, where a change that looks right from one file is right for the whole repo.

## 5. Builder check

Spawn one fresh general-purpose subagent: "Read <spec path> and the code it touches. You must build this without asking anyone. List every question you'd need answered, nothing else." Sort its questions into three groups:

- **Answered** by the spec or the code: fix the spec's wording.
- **Minor:** decide it and mark it as the agent's call.
- **The user's:** it would change behaviour a done check tests. Put these in your approval message.

One round only.

## 6. Approval

Show the spec path, a five-line summary and the user's questions. On "go", or any clear approval, invoke the `ngoi:build` skill with the spec path. Approval covers the whole spec, every unit included.
