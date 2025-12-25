---
name: search
description: Search for notes in the Obsidian vault by content, tags, or frontmatter
---

# Vault Search Skill

This skill helps you search through the Obsidian vault efficiently.

## Capabilities

- Search note content using grep/ripgrep
- Find notes by tags
- Query frontmatter metadata
- Search by filename patterns

## Vault Location

**IMPORTANT:** Always read the vault path from `config.yaml` first:

```bash
# Read vault path from config (requires yq or python)
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
```

Or check `config.yaml` to see the configured path.

## Common Search Patterns

### Search for content in all notes
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -r "search term" "$VAULT_PATH" --include="*.md"
```

### Find notes with specific tags
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -r "^tags:.*tag-name" "$VAULT_PATH" --include="*.md"
```

### Search excluding .obsidian folder
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
grep -r "search term" "$VAULT_PATH" --include="*.md" --exclude-dir=".obsidian"
```

### Find notes by filename pattern
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
find "$VAULT_PATH" -name "*pattern*.md" -not -path "*/.obsidian/*"
```

## Using the Search Tool

If the `vault_search.py` tool exists in the `tools/` directory, you can use it:

```bash
python tools/vault_search.py "search term"
```

## Notes

- Always exclude the `.obsidian/` folder from searches (it contains app config)
- The vault uses standard Markdown files with `.md` extension
- Some notes may have YAML frontmatter
- Wikilinks use the format `[[Note Name]]`
