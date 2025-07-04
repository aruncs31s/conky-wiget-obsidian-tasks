#!/usr/bin/env python3

import os
import re
import sys
from datetime import datetime, date, timedelta

def get_obsidian_tasks(notes_dir):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) # Monday as start of week
    end_of_week = start_of_week + timedelta(days=6)
    start_of_month = today.replace(day=1)
    # Calculate end of month: go to next month, then subtract one day
    end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    overdue_tasks = []
    today_tasks = []
    coming_tasks = [] # Tasks this week, but not today
    this_month_tasks = [] # Tasks this month, but not today, overdue, or coming this week

    for root, _, files in os.walk(notes_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("- [ ]"):
                                task_text = line.strip().replace("- [ ] ", "")
                                
                                # Extract date from task (e.g., 2025-07-04)
                                date_match = re.search(r'\d{4}-\d{2}-\d{2}', task_text)
                                task_date = None
                                if date_match:
                                    try:
                                        task_date = datetime.strptime(date_match.group(0), '%Y-%m-%d').date()
                                    except ValueError:
                                        pass # Invalid date format, ignore

                                # Remove links and dates from the displayed task text
                                formatted_task = re.sub(r'https?://\S+', '', task_text)
                                if date_match:
                                    formatted_task = formatted_task.replace(date_match.group(0), '').strip()
                                
                                # Escape Conky special characters like $
                                formatted_task = formatted_task.replace('$', '\$')

                                if task_date:
                                    if task_date < today:
                                        overdue_tasks.append(formatted_task)
                                    elif task_date == today:
                                        today_tasks.append(formatted_task)
                                    elif today < task_date <= end_of_week:
                                        coming_tasks.append(formatted_task)
                                    elif start_of_month <= task_date <= end_of_month:
                                        this_month_tasks.append(formatted_task)
                                else:
                                    # If no date is found, categorize as 'coming' if it's a general task
                                    # or you can choose to ignore it or put it in a 'misc' category
                                    # For now, I'll put it in 'coming' if no date is specified.
                                    coming_tasks.append(formatted_task)

                except Exception as e:
                    print(f"ERROR: Reading {file_path}: {e}", file=sys.stderr)
                    pass  # Silently skip files that can't be read

    return overdue_tasks, today_tasks, coming_tasks, this_month_tasks


if __name__ == "__main__":
    notes_folder = os.path.expanduser("~/Notes")  # Assuming ~/Notes as the default

    # If a path is provided as an argument, use it
    if len(sys.argv) > 1:
        notes_folder = sys.argv[1]

    overdue_tasks, today_tasks, coming_tasks, this_month_tasks = get_obsidian_tasks(notes_folder)

    # Overdue Tasks
    if overdue_tasks:
        print("${color1}${alignc}O V E R D U E   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in overdue_tasks[:5]:  # Limit to 5 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   O V E R D U E   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")

    print("\n")  # Add a newline for separation

    # Today's Tasks
    if today_tasks:
        print("${color1}${alignc}T O D A Y ' S   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in today_tasks[:5]:  # Limit to 5 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   T O D A Y ' S   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")

    print("\n")  # Add a newline for separation

    # Coming Tasks (this week)
    if coming_tasks:
        print("${color1}${alignc}C O M I N G   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in coming_tasks[:5]:  # Limit to 5 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   C O M I N G   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")

    print("\n")  # Add a newline for separation

    # This Month's Tasks
    if this_month_tasks:
        print("${color1}${alignc}T H I S   M O N T H ' S   T A S K S${color}")
        print("${color1}${hr}${color}")
        for task in this_month_tasks[:5]:  # Limit to 5 tasks
            print(f"${{color1}}• ${{color2}}{task}${{color}}")
    else:
        print("${{color1}}${{alignc}}N O   T H I S   M O N T H ' S   T A S K S${{color}}")
        print("${{color1}}${{hr}}${{color}}")