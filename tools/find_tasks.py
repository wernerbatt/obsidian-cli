#!/usr/bin/env python3
"""
Find tasks in Obsidian vault matching "To Process" criteria.

Usage:
    python tools/find_tasks.py
    python tools/find_tasks.py --query "to-process"
    python tools/find_tasks.py --set-scheduled 2025-12-22
"""

import argparse
import re
from pathlib import Path
from datetime import datetime, date
import yaml
import shutil


def load_config():
    """Load configuration to find vault path."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    vault_path = Path(__file__).parent.parent / config['vault_path']
    return vault_path.resolve()


def parse_task_line(line, line_num):
    """Parse a task line and extract metadata."""
    # Basic task pattern: - [ ] or - [x]
    task_match = re.match(r'^(\s*)- \[(.)\]\s+(.*)$', line)
    if not task_match:
        return None

    indent, status, description = task_match.groups()
    is_done = status.lower() != ' '

    # Extract Obsidian Tasks metadata
    due_date = None
    scheduled_date = None

    # Due date: 📅 YYYY-MM-DD or 📆 YYYY-MM-DD
    due_match = re.search(r'[📅📆]\s*(\d{4}-\d{2}-\d{2})', description)
    if due_match:
        try:
            due_date = datetime.strptime(due_match.group(1), '%Y-%m-%d').date()
        except:
            pass

    # Scheduled date: ⏳ YYYY-MM-DD
    sched_match = re.search(r'⏳\s*(\d{4}-\d{2}-\d{2})', description)
    if sched_match:
        try:
            scheduled_date = datetime.strptime(sched_match.group(1), '%Y-%m-%d').date()
        except:
            pass

    # Check for blocking (tasks with dependencies)
    is_blocked = '⛔' in description or '🔁' in description

    return {
        'line_num': line_num,
        'description': description.strip(),
        'is_done': is_done,
        'due_date': due_date,
        'scheduled_date': scheduled_date,
        'is_blocked': is_blocked,
        'indent': len(indent)
    }


def matches_to_process_criteria(task, file_path):
    """Check if task matches 'To Process' criteria."""
    desc = task['description']
    path_str = str(file_path)

    # Exclusion: description includes context tags
    excluded_tags = ['@pc', '@work', '@home', '@sharne', '@out',
                     '@garden', '@someday', '@ai', '@ponderables', '@stuck']
    for tag in excluded_tags:
        if tag in desc:
            return False

    # Exclusion: time range pattern (HH:MM - HH:MM)
    if re.match(r'^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', desc):
        return False

    # Exclusion: empty description
    if re.match(r'^$', desc):
        return False

    # Exclusion: path includes certain folders
    excluded_paths = ['Checklist', 'Templates', 'Recurring', 'obsidian-tasks']
    for excluded in excluded_paths:
        if excluded in path_str:
            return False

    # Date filters: (no due date) OR (due before today)
    today = date.today()
    if task['due_date'] is not None and task['due_date'] >= today:
        return False

    # Date filters: (no scheduled date) OR (scheduled before today)
    if task['scheduled_date'] is not None and task['scheduled_date'] >= today:
        return False

    # Status filters
    if task['is_blocked']:
        return False

    if task['is_done']:
        return False

    return True


def find_tasks(vault_path, query_type='to-process'):
    """Find tasks in vault."""
    tasks = []

    for md_file in vault_path.rglob("*.md"):
        # Skip .obsidian folder
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                task = parse_task_line(line, line_num)
                if not task:
                    continue

                # Apply query filter
                if query_type == 'to-process':
                    if not matches_to_process_criteria(task, md_file):
                        continue
                elif query_type == 'all':
                    if task['is_done']:
                        continue

                tasks.append({
                    'file': md_file,
                    'file_relative': md_file.relative_to(vault_path),
                    'line_num': line_num,
                    'description': task['description'],
                    'due_date': task['due_date'],
                    'scheduled_date': task['scheduled_date']
                })

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    # Sort by path reverse (as specified)
    tasks.sort(key=lambda x: str(x['file_relative']), reverse=True)

    return tasks


def add_scheduled_date_to_task(description, scheduled_date):
    """Add or update scheduled date in task description."""
    # Remove existing scheduled date if present
    description = re.sub(r'⏳\s*\d{4}-\d{2}-\d{2}', '', description).strip()

    # Add new scheduled date at the end
    return f"{description} ⏳ {scheduled_date}"


def update_tasks_with_scheduled_date(tasks, scheduled_date_str, vault_path, create_backup=True):
    """Update tasks with a scheduled date."""
    # Group tasks by file
    tasks_by_file = {}
    for task in tasks:
        file_path = task['file']
        if file_path not in tasks_by_file:
            tasks_by_file[file_path] = []
        tasks_by_file[file_path].append(task)

    updated_count = 0

    for file_path, file_tasks in tasks_by_file.items():
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Create backup if requested
            if create_backup:
                backup_path = file_path.with_suffix('.md.bak')
                shutil.copy2(file_path, backup_path)

            # Update tasks (reverse order to preserve line numbers)
            for task in sorted(file_tasks, key=lambda t: t['line_num'], reverse=True):
                line_idx = task['line_num'] - 1
                original_line = lines[line_idx]

                # Parse the task line to get structure
                task_match = re.match(r'^(\s*- \[.\]\s+)(.*)$', original_line)
                if task_match:
                    prefix, description = task_match.groups()
                    new_description = add_scheduled_date_to_task(description.rstrip(), scheduled_date_str)
                    lines[line_idx] = f"{prefix}{new_description}\n"
                    updated_count += 1

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"Updated {len(file_tasks)} task(s) in {file_path.relative_to(vault_path)}")

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

    return updated_count


def main():
    parser = argparse.ArgumentParser(description="Find tasks in Obsidian vault")
    parser.add_argument("--query", default="to-process",
                       choices=['to-process', 'all'],
                       help="Query type (default: to-process)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed task information")
    parser.add_argument("--set-scheduled", metavar="DATE",
                       help="Set scheduled date on found tasks (format: YYYY-MM-DD)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup files when updating tasks")

    args = parser.parse_args()

    vault_path = load_config()
    tasks = find_tasks(vault_path, args.query)

    print(f"Found {len(tasks)} tasks:")
    print()

    # If setting scheduled date, do that and exit
    if args.set_scheduled:
        # Validate date format
        try:
            datetime.strptime(args.set_scheduled, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{args.set_scheduled}'. Use YYYY-MM-DD")
            return

        print(f"Setting scheduled date to {args.set_scheduled} for {len(tasks)} tasks...")
        print()

        updated = update_tasks_with_scheduled_date(
            tasks,
            args.set_scheduled,
            vault_path,
            create_backup=not args.no_backup
        )

        print()
        print(f"Successfully updated {updated} tasks!")
        if not args.no_backup:
            print("Backup files created with .bak extension")
        return

    # Otherwise, just display tasks
    current_file = None
    for task in tasks:
        # Group by file
        if task['file_relative'] != current_file:
            current_file = task['file_relative']
            print(f"\n{task['file_relative']}:")

        # Show task
        task_str = f"  Line {task['line_num']}: {task['description']}"

        if args.verbose:
            if task['due_date']:
                task_str += f" [Due: {task['due_date']}]"
            if task['scheduled_date']:
                task_str += f" [Scheduled: {task['scheduled_date']}]"

        print(task_str)


if __name__ == "__main__":
    main()
