# Antigravity Agent Configuration (GEMINI.md)

This file serves as the central nervous system and single source of truth for the Antigravity AI agent. It defines behavioral rules, project specifications, and alignment guidelines.

## 1. Core Behavioral Rules

**1. Think Before Coding**
Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

**2. Simplicity First**
Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

**3. Surgical Changes**
Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.
- The test: Every changed line should trace directly to the user's request.

**4. Goal-Driven Execution**
Define success criteria. Loop until verified.

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## 2. Project Context & Specifications
*(Update this section for specific projects to align the agent with project goals)*

- **Primary Goal:** [Insert primary project goal here]
- **Key Features:** [List main features]
- **Data Models:** [Describe core entities or schema]
- **Success Criteria:** [Define how to measure project success]

---

## 3. Technology Stack & Preferences
*(Define global or project-specific technical constraints here)*

- **Languages:** [e.g., Python, TypeScript]
- **Frameworks:** [e.g., React, Next.js, Django]
- **Testing:** [e.g., Pytest, Jest]
- **Formatting/Linting:** [Follow existing project conventions by default]

---

## 4. Agent Alignment & Internal Workflow
- **File Interrogation:** Always inspect a file before attempting to write or replace content within it.
- **Specific Tools:** Always prioritize the most specific built-in tools (e.g., `grep_search` or `list_dir` over running raw terminal commands).
- **Communication:** Provide concise summaries of work completed. Use GitHub-style markdown for structured, readable responses.
