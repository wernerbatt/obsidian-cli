---
name: meal-plan
description: Plan weekly meals using recipes from the Obsidian vault and add them to Google Calendar. Searches vault for recipe inspiration, iterates with the user to lock in choices, then creates calendar events with ingredients and prep instructions. Use when asked to plan meals, create a meal plan, or organise dinners for the week.
---

# Meal Plan

Plan a week of meals (Sunday→Saturday), drawing from the Obsidian recipe collection and the user's own suggestions, then publish to Google Calendar.

## Setup

Requires:
- `gccli` (Google Calendar CLI) — already configured with an account
- Access to the Obsidian vault

## Constants

```
VAULT_PATH   = Read from config.yaml: vault_path

EMAIL        = Read from config.yaml: settings.email
CALENDAR_ID  = Read from config.yaml: settings.calendar_id
TEMPLATES    = Read settings.templates_folder from config.yaml
               Fallback: Templates
```

## User Preferences

These are standing preferences — apply them automatically without asking.

### Always in the pantry (never add to shopping list)
- Salt, black pepper, sugar
- Olive oil, vegetable/neutral oil, butter
- Garlic
- Cumin, cayenne, chilli powder, dried oregano, curry powder, onion powder
- Dried rosemary, dried thyme, dried tarragon
- Soy sauce, dark soy sauce, rice vinegar, toasted sesame oil, honey
- Fish sauce, Shaoxing rice wine, hoisin sauce, gochujang
- Sesame seeds, sriracha, hot sauce
- Kewpie mayo, cooking spray
- Parmigiano Reggiano
- Frozen ginger (never fresh ginger)
- Knorr chicken stock cubes, vegetable stock mix
- Dijon mustard, cornstarch, sumac
- Greek yoghurt
- Dry white wine (cooking)
- Lime juice, lemon juice (bottled, always in fridge)

### Substitution rules
- **Fresh rosemary / fresh thyme** → always swap to dried (pantry staple)
- **Fresh ginger** → always swap to frozen ginger (pantry staple)
- **Beef bouillon paste** → swap to Knorr Beef Stock Pots
- **Guajillo / specialty chile powder** → swap to regular chilli powder
- **Cilantro** → call it "fresh coriander" (UK naming)
- **Chopped tomatoes / tinned tomatoes** → interchangeable, just call it "tinned tomatoes"

### Shopping list rules
- Always check how many **brown onions** and **red onions** are needed across all meals — add to "CHECK AT HOME" section
- **Limes / lemons** — if only needed for juice, skip (bottled juice always in fridge). Only add to buy list if recipe needs zest or wedges to serve
- **Soup** — user always buys prepped soup, never homemade. Don't list soup ingredients; just note "shop-bought soup" on the calendar event
- **No turkey/chicken breast slices** for sandwich fillings
- Quantities: always specify amounts (e.g. "Fresh coriander, 1 small bunch" not just "Fresh coriander")

## Household Context

### Work patterns
- **Werner**: works from office Monday & Thursday. WFH other weekdays. Can cook midday on WFH days.
- **Partner**: shift worker. Check their calendar for each week's pattern.

### Cooking logistics
- Always plan meals for both — **no solo meals**.
- On partner's late-shift days: meal must be cooked before they leave (they eat before going, or take it).
- On partner's early-shift days: they're back by ~15:30, normal evening dinner works.
- Werner can't cook midday on office days (Mon, Thu). If a meal is needed for a Mon/Tue shift, someone cooks the day before or on a day off.
- Partner often batch-cooks on days off for upcoming shifts.

### Serving size
- **Default: serves 2.** If a recipe serves more, flag it and ask:
  - Halve it for 2?
  - Keep full for leftovers? (only if the meal reheats well)
- **Salmon** does not reheat well — always scale to exact portions.
- **Salmon fillets**: specify as count (e.g. "2 salmon fillets") not weight.
- Curries, stews, pasta bakes, rice bowls reheat well — good leftover candidates.

## Workflow

### 1. Determine the week

- Default: the current week, Sunday→Saturday.
- Calculate dates for all 7 days (YYYY-MM-DD).
- If the user specifies "next week" or a date range, adjust accordingly.

### 2. Check calendars

Check the **Family** calendar for existing meal events:
```bash
gccli $EMAIL events $CALENDAR_ID --from <sunday>T00:00:00Z --to <saturday>T23:59:59Z --max 50
```

Check **partner's calendar** for work shifts:
```bash
gccli $EMAIL events $PARTNER_EMAIL --from <sunday>T00:00:00Z --to <saturday>T23:59:59Z --max 50
```

- Note any existing meal events so we don't double-book.
- Map out partner's shifts (early/late/off) for each day.
- Show the user what's already planned and the shift pattern.

### 3. Search Obsidian for recipe inspiration

```bash
grep -rl '\[\[Recipes\]\]' "$VAULT_PATH" --include="*.md" --exclude-dir=".obsidian"
```

- Build a list of available recipes from the vault.
- Use recipe names (filenames) to suggest meals.
- A mix of vault recipes and free suggestions is fine — the user may want both.

### 4. Suggest and iterate

- Propose a meal for each empty day, aiming for variety (chicken, beef, fish, pork, veggie, pasta, etc.).
- Present the full week as a table with a **"Cook When"** column showing who cooks and when, based on shift patterns and office days.
- The user will **lock in** days they like and **swap** the rest.
- Repeat until all 7 days are confirmed.
- Be responsive to user preferences: "give me a rice bowl", "I want pasta", "swap", etc.

### 5. Create calendar events

For each confirmed meal (skip days that already have events):

```bash
gccli $EMAIL create $CALENDAR_ID \
  --summary "<MEAL NAME IN ALL CAPS>" \
  --start <date>T12:00:00Z \
  --end <date>T12:30:00Z \
  --description "<description>"
```

**Event format:**
- **Summary**: ALL CAPS meal name
- **Time**: 12:00 noon UTC, 30-minute slot
- **Description** must include:
  1. Recipe URL (if available from the vault note's `url` or `source` frontmatter field)
  2. `INGREDIENTS:` — full ingredient list from the recipe
  3. `PREP:` — super brief prep summary (3-5 sentences max)

To build the description, read each recipe's vault note to extract ingredients, directions, and URL.

### 6. Update the `last` field in Obsidian recipe notes

For every meal that has a matching recipe file in the vault, update the `last` frontmatter field to the planned date:

```bash
# Find the line and replace it
sed -i "s/^last:.*/last: <YYYY-MM-DD>/" "$VAULT_PATH/References/<Recipe Name>.md"
```

Also check `Clippings/` if the recipe lives there instead of `References/`.

### 7. Create recipe files for meals not in Obsidian

If a confirmed meal does NOT have an existing recipe note in the vault:

1. Copy the Recipe Template:
```bash
cp "$VAULT_PATH/$TEMPLATES/Recipe Template.md" "$VAULT_PATH/References/<Meal Name>.md"
```

2. Fill in the frontmatter:
   - `category: - "[[Recipes]]"`
   - `created`: today's date (YYYY-MM-DD)
   - `last`: the planned date (YYYY-MM-DD)
   - `tags: - recipes`
   - `cuisine`, `type`, `ingredients`: populate based on what you know about the meal
   - `url`: include if the user provided one or you found one

3. Fill in the body:
   - `## Ingredients` — list all ingredients
   - `## Directions` — write out the steps
   - `## Notes` — any tips or source info

### 8. Compile shopping list

After locking in meals and creating calendar events, compile a shopping list:

1. **Gather all ingredients** from every confirmed meal's recipe.
2. **Apply substitution rules** (see User Preferences above).
3. **Remove pantry staples** (see "Always in the pantry" list above).
4. **Consolidate duplicates** — combine the same ingredient across meals (e.g. spaghetti total across two meals, not listed twice).
5. **Count onions** — tally brown onions and red onions needed across all meals.
6. **Label items with short meal description** — use e.g. "(brothy rice)" not "(Mon)" or "(Monday)".
6. **Categorise** into sections:
   - MEAT & FISH
   - FRESH VEG & HERBS
   - DAIRY & CHEESE
   - BREAD & TORTILLAS
   - SPECIALTY
   - PANTRY (top up if low)
   - CHECK AT HOME (miso, onions, anything uncertain)

7. **Present to the user** for review. Iterate — they will tell you what they already have, what to swap, etc.

8. **Copy to clipboard** when confirmed, using this format (no special characters, no empty lines, `===SECTION===` headers):

```bash
printf "===MEAT & FISH===\r\nItem 1\r\nItem 2\r\n===FRESH VEG & HERBS===\r\nItem 3\r\n..." | clip.exe
```

- Use `\r\n` line endings (Windows clipboard)
- No checkboxes or special Unicode — plain ASCII only
- Each item on its own line so Google Keep creates individual checkboxes
- No empty lines between sections

## Example interaction

```
User: plan meals for this week

Agent: [checks calendar, finds RACLETTE on Monday]
       [searches vault for recipes]
       [suggests 6 meals for the empty days]

User: lock in tuesday and friday. swap the rest

Agent: [proposes new meals for the swapped days]

User: looks good, add to calendar

Agent: [creates events with ingredients & prep]
       [updates `last` field on vault recipes]
       [creates new recipe files for any non-vault meals]
       [compiles shopping list, presents for review]

User: I already have the salmon. move coriander to fresh veg

Agent: [updates list, copies to clipboard]
```

## Notes

- Always read recipe notes before creating events — don't guess at ingredients.
- For free suggestions (not from vault), use common knowledge to write a reasonable ingredient list and prep.
- Keep the description concise — it needs to be readable on a phone calendar.
- Respect existing calendar events — don't overwrite them unless asked.
- Always specify quantities on the shopping list — count items across all meals.
- Use UK English for ingredient names (coriander not cilantro, spring onions not scallions, etc.).
