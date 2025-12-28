---
name: tasks
description: Find and manage tasks in the Obsidian vault using Obsidian Tasks format
---

# Tasks Skill

This skill helps you work with tasks in your Obsidian vault, using the Obsidian Tasks plugin format.

## Task Format

Tasks in Obsidian use standard Markdown checkboxes with metadata:

```markdown
- [ ] Task description 📅 2025-12-22 ⏳ 2025-12-20
- [x] Completed task
```

### Task Metadata

- `📅` or `📆` - Due date
- `⏳` - Scheduled date
- `🛫` - Start date
- `✅` - Done date
- `🔁` - Recurring task
- `⛔` - Blocked/dependency

### Context Tags

Tasks can be tagged with context:
- `@pc` - Requires computer
- `@work` - Work context
- `@home` - Home context
- `@sharne` - Requires Sharne
- `@out` - Outside/errands
- `@garden` - Garden work
- `@someday` - Someday/maybe
- `@ai` - AI-related
- `@ponderables` - Things to think about
- `@stuck` - Blocked/stuck tasks

## Finding Tasks

### Use the find_tasks.py Tool

```bash
# Find all "To Process" tasks (no context, overdue/unscheduled)
python tools/find_tasks.py

# Find all incomplete tasks
python tools/find_tasks.py --query all

# Show detailed info (dates)
python tools/find_tasks.py --verbose
```

### "To Process" Query Logic

The default query finds tasks that:
- ✅ Have NO context tags (@pc, @work, @home, etc.)
- ✅ Are NOT time blocks (HH:MM - HH:MM format)
- ✅ Have non-empty descriptions
- ✅ Are NOT in excluded folders (Checklist, Templates, Recurring, obsidian-tasks)
- ✅ Have NO due date OR are overdue (due before today)
- ✅ Have NO scheduled date OR are overdue scheduled
- ✅ Are NOT blocked (⛔)
- ✅ Are NOT done

Results are sorted by path (reverse alphabetical).

## Manual Search

### Find all incomplete tasks
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -r "^- \[ \]" "$VAULT_PATH" --include="*.md" --exclude-dir=".obsidian"
```

### Find tasks with specific context
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -r "^- \[ \].*@pc" "$VAULT_PATH" --include="*.md"
```

### Find overdue tasks
```bash
python tools/find_tasks.py --query to-process
```

## Best Practices

- Use context tags to organize tasks by location/resources needed
- Add due dates for time-sensitive tasks
- Use scheduled dates for when you plan to work on tasks
- Keep "To Process" query clean by adding context to all tasks
- Time blocks (HH:MM - HH:MM) are automatically excluded from processing
