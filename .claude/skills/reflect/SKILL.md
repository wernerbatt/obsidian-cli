---
name: reflect
description: Analyze the current session and propose improvements to skills. Run after using a skill to capture learnings.
---

| name    | description                                                                                                                                                                                                        |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| reflect | Analyze the current session and propose improvements to skills. Run after using a skill to capture learnings. Use when user says "reflect", "improve skill", "learn from this", or at end of skill-heavy sessions. |

# Reflect Skill

Analyze the current conversation and propose improvements to skills based on what worked, what didn't, and edge cases discovered.

## Trigger

Run `/reflect` or `/reflect [skill-name]` after a session where you used a skill.

## Workflow

### Step 1: Identify the Skill

If skill name not provided, ask:

```
Which skill should I analyze this session for?
- frontend-design
- code-reviewer
- [other]
```

If the user explicitly names a skill (for example, `/reflect on reference`), skip the prompt and proceed with that skill.

### Step 2: Analyze the Conversation

Look for these signals in the current conversation:

Corrections (HIGH confidence):
- User said "no", "not like that", "I meant..."
- User explicitly corrected output
- User asked for changes immediately after generation

Successes (MEDIUM confidence):
- User said "perfect", "great", "yes", "exactly"
- User accepted output without modification
- User built on top of the output

Edge Cases (MEDIUM confidence):
- Questions the skill didn't anticipate
- Scenarios requiring workarounds
- Features user asked for that weren't covered

Preferences (accumulate over sessions):
- Repeated patterns in user choices
- Style preferences shown implicitly
- Tool/framework preferences

### Step 3: Propose Changes

Present findings using accessible colors (WCAG AA 4.5:1 contrast ratio).
Pad each line to a fixed width so the right border stays aligned.
Emoji bullets are double-width in many terminals; add one extra trailing space
on lines that include 🔴/🟡/🔵 to keep the right border straight.
Empty spacer lines need one extra space to match the emoji line width.
Bottom border needs one extra dash to align with the right edge.
Keep the Commit line within the box width; if it’s too long, wrap to a
continuation line with the same left border and pad to the right edge.

```
┌─ Skill Reflection: [skill-name] ──────────────────────────────┐
│                                                                │
│ Signals: X corrections, Y successes                            │
│                                                                │
│ Proposed changes:                                              │
│                                                                │
│ 🔴 [HIGH] + Add constraint: "[specific constraint]"           │
│ 🟡 [MED]  + Add preference: "[specific preference]"           │
│ 🔵 [LOW]  ~ Note for review: "[observation]"                  │
│                                                                │
│ Commit: "[skill]: [summary of changes]"                        │
│         "[continuation if needed]"                             │
└────────────────────────────────────────────────────────────────┘
```

Apply these changes? [Y/n] or describe tweaks

Accessible Color Palette (use ANSI codes in terminal output):
- HIGH: \033[1;31m (bold red #FF6B6B - 4.5:1 on dark)
- MED: \033[1;33m (bold yellow #FFE066 - 4.8:1 on dark)
- LOW: \033[1;36m (bold cyan #6BC5FF - 4.6:1 on dark)
- Reset: \033[0m

Avoid: pure red (#FF0000) on black, green on red (colorblind users)

- Y — Apply changes, commit, and push
- n — Skip this update
- Or describe any tweaks to the proposed changes

### Step 4: If Approved

1. Locate the skills root in this order:
   - `$CODEX_HOME/skills` (preferred)
   - `~/.codex/skills`
   - `.claude/skills` within the current repo (if present)
2. Read the current skill file from `[skills-root]/[skill-name]/SKILL.md`
3. Apply the changes using the Edit tool
4. If the skill path is a symlink, resolve the real path and use its repo for git operations.
5. Run git commands from the skills root (if it is a git repo):

```
cd [skills-root]
git add [skill-name]/SKILL.md
git commit -m "[skill]: [change summary]"
git push origin main
```

6. Confirm: "Skill updated and pushed to GitHub" and mention the symlink target if one was used.

### Step 5: If Declined

Ask: "Would you like to save these observations for later review?"

If yes, append to `~/.claude/skills/[skill-name]/OBSERVATIONS.md`

## Example Session

User runs `/reflect frontend-design` after a UI session:

```
┌─ Skill Reflection: frontend-design ────────────────────────────┐
│                                                                │
│ Signals: 2 corrections, 3 successes                             │
│                                                                │
│ Proposed changes:                                               │
│                                                                │
│ 🔴 [HIGH] + Constraints/NEVER:                                │
│     "Use gradients unless explicitly requested"               │
│                                                                │
│ 🔴 [HIGH] + Color & Theme:                                    │
│     "Dark backgrounds: use #000, not #1a1a1a"                 │
│                                                                │
│ 🟡 [MED]  + Layout:                                           │
│     "Prefer CSS Grid for card layouts"                       │
│                                                                │
│ Commit: "frontend-design: no gradients, #000 dark"              │
└────────────────────────────────────────────────────────────────┘
```

Apply these changes? [Y/n] or describe tweaks

## Git Integration

This skill has permission to:
- Read skill files from the active skills root (`$CODEX_HOME/skills`, `~/.codex/skills`, or repo-local `.claude/skills`)
- Edit skill files (with user approval)
- Run `git add`, `git commit`, `git push` in the skills root when it is a git repo

The skills repo should be initialized at the active skills root with a remote origin.

## Important Notes

- Always show the exact changes before applying
- Never modify skills without explicit user approval
- Commit messages should be concise and descriptive
- Push only after successful commit
