# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit pet care scheduling app that helps an owner organize daily care tasks for multiple pets. The project uses object-oriented design to model pets and tasks, builds a daily plan with priority-based scheduling, detects conflicts, explains the result, and now includes a few optional extensions such as JSON persistence, next-available-slot suggestions, emoji priority styling, and a cleaner CLI demo.

## Project Goal

The goal of this project is to build a smart pet care management system that helps a busy owner stay consistent with pet responsibilities such as walks, feeding, grooming, enrichment, and medication.

This project demonstrates:

- object-oriented design in Python
- modular system design
- scheduling logic using sorting and filtering
- recurrence handling for daily and weekly tasks
- exact-time conflict detection
- Streamlit UI integration
- automated testing with pytest
- optional persistence and smart scheduling extensions

## Features

### Core features
- Add and manage multiple pets
- Add tasks with title, date, time, duration, priority, and frequency
- Generate a daily schedule for a selected date
- Sort tasks by priority first, then by time
- Detect exact-time task conflicts
- Automatically support recurring daily and weekly tasks
- Show a readable explanation of how the schedule was built

### Optional extensions completed
- **Data persistence with `data.json`** so pets and tasks can be loaded between runs
- **`save_to_json()` and `load_from_json()`** methods on the `Owner` class
- **Next available slot suggestion** that scans the day in 15-minute steps
- **Emoji priority/status formatting** in the Streamlit UI
- **Structured CLI output** in `main.py` using `tabulate`
- **Prompt comparison reflection section** documenting what a multi-model comparison would focus on and why one style felt more Pythonic

## Core Classes

### `Task`
Represents one pet care task.
Stores:
- title
- time of day
- duration
- priority
- frequency
- due date
- completion status
- pet name

### `Pet`
Represents a single pet and stores a list of tasks.

### `Owner`
Represents the owner and stores multiple pets. It also handles JSON persistence.

### `Scheduler`
Builds the daily plan by:
- gathering tasks
- filtering by date
- sorting by priority and time
- detecting conflicts
- explaining the schedule
- suggesting the next available slot

## Scheduling Logic

The scheduler uses a simple rule-based approach:

1. collect all tasks from all pets
2. filter tasks for the selected date
3. sort by priority:
   - high
   - medium
   - low
4. sort by time within each priority bucket
5. detect tasks that happen at the exact same time
6. return the ordered schedule and explanation

### Optional algorithmic extension: Next available slot

The next-available-slot feature looks at the tasks already scheduled on a selected date and treats each one as a time interval using its duration. It then scans the day in 15-minute steps and returns the earliest open slot that fits the requested duration.

## Tradeoff

Conflict detection still checks only for **exact matching start times**, not overlapping durations. I kept this as the main conflict rule because it is easier to explain and test. The next-available-slot algorithm handles durations more directly, which gives the app one smarter feature without making the main schedule builder too complex.

## Optional Extension Notes (AI / Agent-style Planning)

For the optional extensions, I used AI in an agent-style way to help break the work into smaller implementation steps. The most useful parts were planning how JSON serialization should work, deciding where persistence methods belonged, and sketching the next-available-slot algorithm before I refined the code by hand. I did not blindly copy suggestions. I reviewed the design and kept the version that felt easiest to explain and maintain.

## Project Structure


ai110-module2show-pawpal-starter-main/
├── app.py
├── main.py
├── pawpal_system.py
├── README.md
├── reflection.md
├── requirements.txt
├── data.json
└── tests/
    └── test_pawpal.py

## Installation

Use Python 3.

```bash
python3 -m pip install -r requirements.txt
```

## Run the Streamlit App

```bash
python3 -m streamlit run app.py
```

## Run the CLI Demo

```bash
python3 main.py
```

## Testing PawPal+

Run tests with:

```bash
python3 -m pytest
```
Video Walkthrough

## Video Walkthrough

## Video Walkthrough

![PawPal+ Demo](assets/Week%204%20Project%20Assignment%20AI%20110.gif)

### What the tests cover
- task addition
- recurring task creation
- scheduling order by priority and time
- exact-time conflict detection
- JSON save/load persistence
- next available slot suggestion

## Confidence Level

**4.5/5 stars**

I am confident that the core scheduler works correctly for common use cases such as adding tasks, ordering them, saving them, and handling recurrence. If I had more time, I would test more edge cases like overlapping-duration conflicts in the main schedule, invalid JSON recovery, editing tasks in the UI, and persistence across larger datasets.

## Example Conflict Scenario

To test conflict detection, add two tasks for the same date and time. For example:

- Broche — Taking a walk — 05:45
- Mochi — Breakfast — 05:45

When you generate the schedule, the app should show a conflict warning.

## Technologies Used

- Python
- Streamlit
- pandas
- pytest
- tabulate
- dataclasses
- datetime
- JSON

## Future Improvements

- allow editing and deleting pets/tasks
- support overlapping-duration conflict detection in the main scheduler
- mark tasks complete directly in the UI
- add colored badges or filters by pet/status
- support user preferences such as “morning tasks first” within the same priority

## Author

James Paek