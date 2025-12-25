#!/usr/bin/env python3
"""
Search tool for Obsidian vault.

Usage:
    python vault_search.py "search term"
    python vault_search.py --tag "tag-name"
    python vault_search.py --filename "pattern"
"""

import argparse
import os
import re
from pathlib import Path
import yaml


def load_config():
    """Load configuration to find vault path."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    vault_path = Path(__file__).parent.parent / config['vault_path']
    return vault_path.resolve()


def search_content(vault_path, query, case_sensitive=False):
    """Search for content in markdown files."""
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(query, flags)

    for md_file in vault_path.rglob("*.md"):
        # Skip .obsidian folder
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if pattern.search(content):
                    # Find matching lines
                    lines = content.split('\n')
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if pattern.search(line):
                            matches.append(f"  Line {i}: {line.strip()}")

                    results.append({
                        'file': md_file.relative_to(vault_path),
                        'matches': matches[:5]  # Limit to first 5 matches
                    })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    return results


def search_by_tag(vault_path, tag):
    """Find notes with a specific tag."""
    results = []

    for md_file in vault_path.rglob("*.md"):
        if ".obsidian" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check frontmatter tags
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        try:
                            frontmatter = yaml.safe_load(parts[1])
                            if 'tags' in frontmatter:
                                tags = frontmatter['tags']
                                if isinstance(tags, str):
                                    tags = [tags]
                                if tag in tags:
                                    results.append(md_file.relative_to(vault_path))
                        except:
                            pass

                # Check inline tags
                if f"#{tag}" in content or f"#{tag} " in content:
                    if md_file.relative_to(vault_path) not in results:
                        results.append(md_file.relative_to(vault_path))
        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    return results


def search_by_filename(vault_path, pattern):
    """Find files matching a filename pattern."""
    results = []

    for md_file in vault_path.rglob(f"*{pattern}*.md"):
        if ".obsidian" not in md_file.parts:
            results.append(md_file.relative_to(vault_path))

    return results


def main():
    parser = argparse.ArgumentParser(description="Search Obsidian vault")
    parser.add_argument("query", nargs='?', help="Search query")
    parser.add_argument("--tag", help="Search by tag")
    parser.add_argument("--filename", help="Search by filename pattern")
    parser.add_argument("-i", "--case-sensitive", action="store_true",
                       help="Case sensitive search")

    args = parser.parse_args()

    vault_path = load_config()

    if args.tag:
        print(f"Searching for tag: #{args.tag}")
        results = search_by_tag(vault_path, args.tag)
        print(f"\nFound {len(results)} notes:")
        for file in results:
            print(f"  - {file}")

    elif args.filename:
        print(f"Searching for filename: *{args.filename}*")
        results = search_by_filename(vault_path, args.filename)
        print(f"\nFound {len(results)} notes:")
        for file in results:
            print(f"  - {file}")

    elif args.query:
        print(f"Searching vault for: {args.query}")
        results = search_content(vault_path, args.query, args.case_sensitive)
        print(f"\nFound {len(results)} notes:")
        for result in results:
            print(f"\n{result['file']}:")
            for match in result['matches']:
                print(match)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
