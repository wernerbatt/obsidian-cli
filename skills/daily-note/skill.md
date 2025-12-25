---
name: daily-note
description: Create and manage daily notes in the Obsidian vault
---

# Daily Note Skill

This skill helps you create and work with daily notes.

## Capabilities

- Create new daily notes with consistent naming
- Add entries to existing daily notes
- Find and reference previous daily notes
- Use templates if configured

## Daily Note Format

Daily notes typically use the format: `YYYY-MM-DD.md`

Example: `2025-12-16.md`

## Creating a Daily Note

**IMPORTANT:** Always read the vault path from `config.yaml` first.

### Basic Creation
```bash
# Read vault path from config
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")

# Get today's date in the right format
today=$(date +%Y-%m-%d)

# Create the note in the vault
touch "${VAULT_PATH}/${today}.md"

# Add basic structure
cat > "${VAULT_PATH}/${today}.md" << 'EOF'
# $(date +%Y-%m-%d)

## Notes

## Tasks

- [ ]

## References

EOF
```

### Check if Today's Note Exists
```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
today=$(date +%Y-%m-%d)
if [ -f "${VAULT_PATH}/${today}.md" ]; then
    echo "Daily note already exists"
else
    echo "Creating new daily note"
fi
```

## Finding Recent Daily Notes

```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
# Find all daily notes (YYYY-MM-DD pattern)
find "$VAULT_PATH" -maxdepth 1 -name "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].md" -type f | sort -r | head -10
```

## Template Location

Check `config.yaml` for the configured templates folder, or use the default structure above.

## Best Practices

- Use consistent date format: `YYYY-MM-DD`
- Store daily notes at vault root or in a dedicated folder
- Link between daily notes using wikilinks: `[[2025-12-15]]`
- Tag daily notes consistently if needed: `#daily-note`
