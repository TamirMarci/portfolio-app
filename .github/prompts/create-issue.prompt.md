# Create Issue

Capture a bug, feature, or improvement quickly while the user is mid-development.

## Objectives
Produce a compact, implementation-ready issue with:
- Title
- TL;DR
- Type
- Priority
- Effort
- Current behavior
- Expected behavior
- Relevant files
- Risks/dependencies
- Acceptance criteria

## Interaction rules
- Ask at most 3 brief questions, only if essential details are missing.
- Prefer one short clarification message over multiple back-and-forth turns.
- If obvious, infer:
  - priority = normal
  - effort = medium
- Search the workspace only if needed to find relevant files.
- Skip web search unless the request clearly needs external best practices.

## Output requirements
- Keep it concise and structured.
- Prefer bullets over paragraphs.
- Max 3 relevant files.
- Acceptance criteria must be testable.
- Make the issue easy to hand off to another coding model.

After generating the issue, output it as a markdown file using this path:

issues/<short-feature-name>.md

Return the full file content ready to save.