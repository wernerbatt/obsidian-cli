#!/usr/bin/env python3
"""
Fix filenames with special characters that prevent syncing.

This tool finds files with problematic characters (backslashes, quotes, angle brackets, etc.)
and renames them to be safe for cross-platform syncing with tools like Syncthing.

Usage:
    python fix_sync_filenames.py --dry-run  # Preview changes without renaming
    python fix_sync_filenames.py            # Actually rename files
    python fix_sync_filenames.py --check    # Only list problematic files
"""

import argparse
import os
import re
from pathlib import Path
import yaml


# Characters that commonly cause syncing issues across platforms
PROBLEMATIC_CHARS = {
    '\\': '-',  # Backslash (path separator on Windows)
    '/': '-',   # Forward slash (path separator)
    ':': '-',   # Colon (reserved on Windows)
    '*': '',    # Asterisk (wildcard)
    '?': '',    # Question mark (wildcard)
    '"': "'",   # Double quote
    '<': '(',   # Less than
    '>': ')',   # Greater than
    '|': '-',   # Pipe
}


def load_config():
    """Load configuration to find vault path."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    vault_path = Path(__file__).parent.parent / config['vault_path']
    return vault_path.resolve()


def has_problematic_chars(filename):
    """Check if filename contains any problematic characters."""
    return any(char in filename for char in PROBLEMATIC_CHARS.keys())


def sanitize_filename(filename):
    """Replace problematic characters with safe alternatives."""
    sanitized = filename
    for bad_char, replacement in PROBLEMATIC_CHARS.items():
        sanitized = sanitized.replace(bad_char, replacement)

    # Remove multiple consecutive spaces/dashes
    sanitized = re.sub(r'[ -]+', ' ', sanitized)
    sanitized = re.sub(r'^[ -]+|[ -]+$', '', sanitized)

    return sanitized


def find_problematic_files(vault_path):
    """Find all files with problematic characters in their names."""
    problematic_files = []

    for file_path in vault_path.rglob("*"):
        # Skip directories and .obsidian folder
        if file_path.is_dir() or ".obsidian" in file_path.parts:
            continue

        # Check if filename has problematic characters
        if has_problematic_chars(file_path.name):
            problematic_files.append(file_path)

    return problematic_files


def preview_changes(files, vault_path):
    """Show what changes would be made."""
    if not files:
        print("No files with problematic characters found!")
        return

    print(f"Found {len(files)} file(s) with problematic characters:\n")

    for file_path in files:
        old_name = file_path.name
        new_name = sanitize_filename(old_name)
        relative_path = file_path.relative_to(vault_path)

        print(f"File: {relative_path}")
        print(f"  Old: {old_name}")
        print(f"  New: {new_name}")

        # Show which characters are problematic
        bad_chars = [c for c in PROBLEMATIC_CHARS.keys() if c in old_name]
        print(f"  Problematic chars: {', '.join(repr(c) for c in bad_chars)}")
        print()


def rename_files(files, vault_path, dry_run=False):
    """Rename files to remove problematic characters."""
    if not files:
        print("No files with problematic characters found!")
        return

    renamed_count = 0
    error_count = 0

    for file_path in files:
        old_name = file_path.name
        new_name = sanitize_filename(old_name)
        new_path = file_path.parent / new_name

        # Skip if the new name is the same (shouldn't happen, but just in case)
        if old_name == new_name:
            continue

        # Check if target file already exists
        if new_path.exists():
            print(f"ERROR: Target already exists: {new_path.relative_to(vault_path)}")
            error_count += 1
            continue

        try:
            if dry_run:
                print(f"Would rename: {file_path.relative_to(vault_path)}")
                print(f"         to: {new_path.relative_to(vault_path)}")
            else:
                file_path.rename(new_path)
                print(f"Renamed: {file_path.relative_to(vault_path)}")
                print(f"     to: {new_path.relative_to(vault_path)}")

            renamed_count += 1

        except Exception as e:
            print(f"ERROR renaming {file_path.relative_to(vault_path)}: {e}")
            error_count += 1

    print(f"\n{'Would rename' if dry_run else 'Renamed'} {renamed_count} file(s)")
    if error_count > 0:
        print(f"Encountered {error_count} error(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Fix filenames with special characters that prevent syncing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually renaming files"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only list problematic files without showing rename preview"
    )

    args = parser.parse_args()

    vault_path = load_config()

    if not vault_path.exists():
        print(f"ERROR: Vault path not found: {vault_path}")
        print("Please check your config.yaml")
        return 1

    print(f"Scanning vault: {vault_path}\n")

    problematic_files = find_problematic_files(vault_path)

    if args.check:
        # Just list the problematic files
        if not problematic_files:
            print("No files with problematic characters found!")
        else:
            print(f"Found {len(problematic_files)} file(s) with problematic characters:\n")
            for file_path in problematic_files:
                relative_path = file_path.relative_to(vault_path)
                bad_chars = [c for c in PROBLEMATIC_CHARS.keys() if c in file_path.name]
                print(f"  - {relative_path}")
                print(f"    Problematic chars: {', '.join(repr(c) for c in bad_chars)}")
    elif args.dry_run:
        preview_changes(problematic_files, vault_path)
    else:
        # Show preview first
        preview_changes(problematic_files, vault_path)

        if problematic_files:
            response = input("\nProceed with renaming? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                print("\nRenaming files...\n")
                rename_files(problematic_files, vault_path, dry_run=False)
            else:
                print("Cancelled.")

    return 0


if __name__ == "__main__":
    exit(main())
