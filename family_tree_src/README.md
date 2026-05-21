# Family Tree Source

This directory is the source of truth for the website family tree.

Edit the data here:

- `family_tree_src/data/tree.json`

Build the public page here:

- `family-tree/index.html`

Use these commands from the repo root:

```bash
python scripts/family_tree.py validate
python scripts/family_tree.py build
```

Clean workflow:

1. Edit `family_tree_src/data/tree.json`.
2. Run `python scripts/family_tree.py validate`.
3. Run `python scripts/family_tree.py build`.
4. Commit both the JSON and the generated HTML.

Optional test run:

```bash
python -m unittest family_tree_src.tests.test_core -v
```

The website no longer needs the old standalone FamilyTree web app codebase.
