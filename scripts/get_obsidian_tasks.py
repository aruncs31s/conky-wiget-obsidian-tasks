#!/usr/bin/env python3

import os
import sys


def get_obsidian_tasks(notes_dir, limit=30):
    tasks = []
    for root, _, files in os.walk(notes_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("- [ ]"):
                                task = line.strip().replace("- [ ] ", "")
                                tasks.append(task)
                                if len(tasks) >= limit:
                                    return tasks
                except Exception as e:
                    # print(f"Error reading {file_path}: {e}", file=sys.stderr)
                    pass  # Silently skip files that can't be read

    return tasks


if __name__ == "__main__":
    notes_folder = os.path.expanduser("~/Notes")  # Assuming ~/Notes as the default

    # If a path is provided as an argument, use it
    if len(sys.argv) > 1:
        notes_folder = sys.argv[1]

    tasks = get_obsidian_tasks(notes_folder, limit=35)

    if tasks:
        print("${color1}${alignc}O B S I D I A N   T A S K S${color}")
        print("${color1}${hr}${color}")
        for i, task in enumerate(tasks):
            # Escape Conky special characters like $
            # formatted_task = task.replace("$", "$")
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   T A S K S   F O U N D${{color}}")
        print("${{color1}}${{hr}}${{color}}")
