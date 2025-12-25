# Obsidian CLI Workspace

A workspace for using LLM CLI tools (Claude Code, Gemini CLI, Codex CLI) to interact with your Obsidian vault through skills and custom tools.

## Structure

```
obsidian-cli/
├── skills/          # LLM skills for vault operations
├── tools/           # Python scripts for vault manipulation
├── config.yaml      # Configuration (points to vault)
└── README.md        # This file
```

## Setup

1. Navigate to this directory:
   ```bash
   cd obsidian-cli
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure you're in the workspace with venv activated:
   ```bash
   cd obsidian-cli
   source venv/bin/activate
   ```

2. Launch your preferred LLM CLI:
   ```bash
   claude    # or gemini, or codex
   ```

3. The LLM will discover available skills and can use the tools to work with your vault.

## Configuration

Edit `config.yaml` to:
- Set the path to your Obsidian vault
- Configure default folders for daily notes, templates, etc.
- Enable/disable backups before modifications

## Skills

Skills are stored in the `skills/` directory. Each skill is a folder containing:
- `skill.md` - Instructions and metadata for the LLM
- Optional scripts and resources

## Tools

Python scripts in the `tools/` directory provide programmatic access to vault operations.

### Available Tools

#### `vault_search.py` - Search your Obsidian vault
Search for content, tags, or filenames in your vault.

```bash
# Search for content
python tools/vault_search.py "search term"

# Search by tag
python tools/vault_search.py --tag "tag-name"

# Search by filename
python tools/vault_search.py --filename "pattern"
```

#### `find_tasks.py` - Find tasks in your vault
Search for task items across your notes.

```bash
python tools/find_tasks.py
```

#### `fix_sync_filenames.py` - Fix filenames with special characters
Find and rename files with characters that prevent syncing (backslashes, quotes, angle brackets, etc.).

```bash
# Check for problematic files only
python tools/fix_sync_filenames.py --check

# Preview changes without renaming
python tools/fix_sync_filenames.py --dry-run

# Rename files (with confirmation prompt)
python tools/fix_sync_filenames.py
```

This tool fixes filenames that contain characters incompatible with cross-platform syncing tools like Syncthing:
- Backslashes (`\`) are replaced with dashes
- Angle brackets (`<>`) are replaced with parentheses
- Double quotes (`"`) are replaced with single quotes
- Other problematic characters (`:*?|`) are sanitized

## Getting Started

See the example skill in `skills/search/` for a template to build your own skills.
