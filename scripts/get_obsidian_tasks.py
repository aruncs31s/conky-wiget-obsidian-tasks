#!/usr/bin/env python3

import os
import re
import sys
from datetime import date, datetime, timedelta

total_nots = 0
task_count = 0
total_folders = 0
total_done_tasks = 0


def get_recent_modified_notes(notes_dir, limit=3):
    """
    Get the most recently modified notes in the specified directory.
    Returns a list of tuples (file_path, last_modified_time).
    """
    recent_notes = []
    for root, _, files in os.walk(notes_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    last_modified_time = os.path.getmtime(file_path)
                    recent_notes.append((file_path, last_modified_time))
                except Exception as e:
                    print(f"ERROR: Reading {file_path}: {e}", file=sys.stderr)
                    pass  # Silently skip files that can't be read

    # Sort by last modified time, descending
    recent_notes.sort(key=lambda x: x[1], reverse=True)

    return recent_notes[:limit]


def get_obsidian_tasks(notes_dir):
    global total_nots
    global task_count
    global total_done_tasks
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday as start of week
    end_of_week = start_of_week + timedelta(days=6)
    start_of_month = today.replace(day=1)
    # Calculate end of month: go to next month, then subtract one day
    end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(
        day=1
    ) - timedelta(days=1)

    overdue_tasks = []
    today_tasks = []
    # this will not include today's tasks , todays tasks have different section
    coming_tasks = []
    this_month_tasks = (
        []
    )  # Tasks this month, but not today, overdue, or coming this week
    for root, _, files in os.walk(notes_dir):
        for file in files:
            if file.endswith(".md"):
                total_nots += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("- [ ]"):
                                task_count += 1
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
                                formatted_task = re.sub(
                                    r"\[.*\]\(.*\)", "", formatted_task
                                )  # Remove Obsidian links
                                if date_match:
                                    formatted_task = formatted_task.replace(
                                        date_match.group(0), ""
                                    ).strip()

                                # Escape Conky special characters like $
                                formatted_task = formatted_task.replace("$", "\\$")

                                if task_date:
                                    if task_date < today:
                                        overdue_tasks.append(formatted_task)
                                    elif task_date == today:
                                        today_tasks.append(formatted_task)
                                    elif today < task_date <= end_of_week:
                                        coming_tasks.append(formatted_task)
                                    elif start_of_month <= task_date <= end_of_month:
                                        this_month_tasks.append(formatted_task)
                                # Tasks without dates are ignored for now
                            if line.strip().startswith("- [x]"):
                                total_done_tasks += 1

                except Exception as e:
                    print(f"ERROR: Reading {file_path}: {e}", file=sys.stderr)
                    pass  # Silently skip files that can't be read

    return overdue_tasks, today_tasks, coming_tasks, this_month_tasks


if __name__ == "__main__":
    notes_folder = os.path.expanduser("~/Notes")  # Assuming ~/Notes as the default
    # If a path is provided as an argument, use it
    if len(sys.argv) > 1:
        notes_folder = sys.argv[1]

    overdue_tasks, today_tasks, coming_tasks, this_month_tasks = get_obsidian_tasks(
        notes_folder
    )

    # Print Vault Stats
    print("${color1}${alignc}O B S I D I A N   T A S K S${color}")
    print("${hr}")
    print(
        f" Total Notes: {total_nots}" if total_nots > 0 else "No Notes Found",
        "${alignr}",
        f"Total Folders {total_folders}" if total_folders > 0 else "Total Folders: 378",
    )
    print(
        "${color1}",
        f"Total Tasks: {task_count} 🏋️‍♂️",
        "${alignr}Completed Tasks: ",
        f"{total_done_tasks} ✅",
        "${color0}",
    )
    # get recent modified notes

    print("${hr}")
    print("${color1}${alignc}R E C E N T   N O T E S${color}")
    print("${hr}")
    recent_notes = get_recent_modified_notes(notes_folder, limit=3)
    if recent_notes:
        for note, mtime in recent_notes:
            # make it format like 10:30 AM
            last_modified = datetime.fromtimestamp(mtime).strftime("%I:%M %p")
            print(f"• {os.path.basename(note)} ", "${alignr}", f"{last_modified}")
    else:
        print("N O   R E C E N T   N O T E S")
    # Overdue Tasks

    print("\n")  # Add a newline for separation
    print("${color1}${alignc}O V E R D U E   T A S K S${color}")
    print("${hr}")
    print("${color2}", f"Total Overdue Tasks {len(overdue_tasks)}", "${color0}")
    if overdue_tasks:
        for task in overdue_tasks[:5]:  # Limit to 5 tasks
            print(f"  {task}")
    else:
        print("N O   O V E R D U E   T A S K S")
        print("${hr}")

    print("\n")  # Add a newline for separation

    # Today's Tasks
    print("${color1}${alignc}T O D A Y ' S   T A S K S${color}")
    print("${hr}")
    if today_tasks:
        print("${color2}", f"Total Today's Tasks {len(today_tasks)}", "${color0}")
        for task in today_tasks[:5]:  # Limit to 5 tasks
            print(f" {task}")
    else:
        print(" 😀 No Tasks")

    print("\n")  # Add a newline for separation

    # Coming Tasks (this week)

    print("${color1}${alignc}C O M I N G   T A S K S${color}")
    print("${hr}")
    if coming_tasks:
        for task in coming_tasks[:5]:  # Limit to 5 tasks
            print(f"• {task}")
    else:
        print("  No Tasks")
