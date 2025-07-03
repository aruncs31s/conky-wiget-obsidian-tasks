#!/usr/bin/env python3

import os
import re
import sys
from datetime import date, datetime, timedelta


def get_obsidian_tasks(notes_dir):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday as start of week
    end_of_week = start_of_week + timedelta(days=6)

    today_tasks = []
    this_week_tasks = []

    for root, _, files in os.walk(notes_dir):
        for file in files:
            if file.endswith(".md"):
                print(file)
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("- [ ]"):
                                task_text = line.strip().replace("- [ ] ", "")

                                # Extract date from task (e.g., 2025-07-04)
                                date_match = re.search(r"\d{4}-\d{2}-\d{2}", task_text)
                                task_date = None
                                if date_match:
                                    try:
                                        task_date = datetime.strptime(
                                            date_match.group(0), "%Y-%m-%d"
                                        ).date()
                                    except ValueError:
                                        pass  # Invalid date format, ignore

                                # Remove links and dates from the displayed task text
                                formatted_task = re.sub(r"https?://\S+", "", task_text)
                                if date_match:
                                    formatted_task = formatted_task.replace(
                                        date_match.group(0), ""
                                    ).strip()

                                # Escape Conky special characters like $ for Conky
                                formatted_task = formatted_task.replace("$", "\\$")

                                if task_date == today:
                                    today_tasks.append(formatted_task)
                                elif (
                                    task_date
                                    and start_of_week <= task_date <= end_of_week
                                ):
                                    this_week_tasks.append(formatted_task)

                except Exception as e:
                    # print(f"Error reading {file_path}: {e}", file=sys.stderr)
                    pass  # Silently skip files that can't be read

    return today_tasks, this_week_tasks


if __name__ == "__main__":
    notes_folder = os.path.expanduser("~/Notes")  # Assuming ~/Notes as the default

    # If a path is provided as an argument, use it
    if len(sys.argv) > 1:
        notes_folder = sys.argv[1]

    today_tasks, this_week_tasks = get_obsidian_tasks(notes_folder)

    if today_tasks:
        print("${color1}${alignc}T O D A Y ' S   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in today_tasks[:10]:  # Limit to 10 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   T O D A Y ' S   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")

    print("\n")  # Add a newline for separation

    if this_week_tasks:
        print("${color1}${alignc}T H I S   W E E K ' S   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in this_week_tasks[:10]:  # Limit to 10 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   T H I S   W E E K ' S   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")
