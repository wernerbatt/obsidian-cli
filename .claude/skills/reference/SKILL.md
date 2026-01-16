---
name: reference
description: Create new reference notes in the Obsidian vault by selecting a template, copying it into References, and filling frontmatter fields (including URLs and images). Use when asked to add a book, place, movie, article, or any other reference note.
---

# Reference

## Read config

- Read `vault_path` and `settings.templates_folder` from `config.yaml`.
- Treat an empty `templates_folder` as `Templates/` at the vault root unless configured otherwise.

## Choose a template

- List available templates dynamically before selecting one.
- Match the request to the closest template (book, movie, restaurant, city, etc.).

Example:

```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
TEMPLATES_FOLDER=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['settings'].get('templates_folder') or 'Templates')")
ls "${VAULT_PATH}/${TEMPLATES_FOLDER}" | rg "Template\.md$"
```

## Create the reference file

- Place reference notes in `References/` under the vault.
- Copy the chosen template into `References/<Reference Name>.md`.
- Do not rename existing reference notes unless the user explicitly asks.
- Ensure the `References/` folder exists.
- After creating the new reference note, open it in Obsidian via the URI handler.

Example:

```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
REFERENCE_NAME="Reference Name"
mkdir -p "${VAULT_PATH}/References"
cp "${VAULT_PATH}/Templates/[Template Name].md" "${VAULT_PATH}/References/${REFERENCE_NAME}.md"
```

Open the new reference in Obsidian (WSL):

```bash
cmd.exe /c start "" "obsidian://open?path=$(wslpath -w \"${VAULT_PATH}/References/${REFERENCE_NAME}.md\")"
```

## Fill frontmatter correctly

- Replace template placeholders (for example, `{{date}}`).
- Set `created` to `YYYY-MM-DD`.
- Keep `last` empty at all times.
- Include `url` in frontmatter when the user provides one.
- Use wikilinks for fields like `category`, `author`, or `loc` when your templates expect them.
- Populate metadata for all fields you have reasonable confidence about (for example: cuisine, type, ingredients, author, url).
- For recipes, prefer a YAML list for `ingredients` when multiple items are known.

## Add images for physical places or visual items

- Look in `Attachments/` for a matching image.
- Add a `cover: "[[Attachments/file.jpg]]"` frontmatter field or embed with `![[Attachments/file.jpg]]`.

## Example: add a restaurant

```bash
VAULT_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['vault_path'])")
mkdir -p "${VAULT_PATH}/References"
cp "${VAULT_PATH}/Templates/Restaurant Template.md" "${VAULT_PATH}/References/Sushi Nakamoto.md"
# Edit frontmatter:
# - category: [[Places]]
# - type: [[Restaurants/Japanese]]
# - loc: [[Tokyo]]
# - tags: places, restaurants, japanese
# - created: 2025-12-28
# - last: (empty)
# - cover: "[[Attachments/sushi-nakamoto.jpg]]" (if available)
```
