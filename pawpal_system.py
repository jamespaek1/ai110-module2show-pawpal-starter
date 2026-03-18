"""PawPal+ core system module with optional extensions.

This module defines the classes and logic for managing pet care tasks and
scheduling them into a daily plan. In addition to the core requirements,
it also includes optional extensions:

- JSON persistence via ``Owner.save_to_json`` and ``Owner.load_from_json``
- a next-available-slot algorithm in ``Scheduler.find_next_available_slot``
- helper serialization methods for Task and Pet
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_DATA_FILE = "data.json"


def _parse_time_string(t: str) -> time:
    """Parse a time in HH:MM 24-hour format into a ``datetime.time`` object."""
    try:
        hour_str, minute_str = t.strip().split(":")
        hour = int(hour_str)
        minute = int(minute_str)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
        return time(hour=hour, minute=minute)
    except Exception as exc:  # pragma: no cover - defensive parsing
        raise ValueError(f"Invalid time format '{t}'. Expected HH:MM.") from exc


def _priority_weight(priority: str) -> int:
    """Return a numeric weight for a priority label."""
    mapping = {"low": 1, "medium": 2, "high": 3}
    return mapping.get(priority.lower(), 0)


def _time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def _minutes_to_time(value: int) -> time:
    return time(hour=value // 60, minute=value % 60)


@dataclass
class Task:
    """Represents a single care task for a pet."""

    title: str
    time_of_day: time
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "once"
    owner_pet: Optional[str] = None
    due_date: date = field(default_factory=date.today)
    is_completed: bool = False

    @property
    def priority_weight(self) -> int:
        """Return the numeric weight of the task priority."""
        return _priority_weight(self.priority)

    def mark_complete(self) -> Optional["Task"]:
        """Mark the task complete and create the next recurring task if needed."""
        self.is_completed = True
        if self.frequency == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            time_of_day=self.time_of_day,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            owner_pet=self.owner_pet,
            due_date=next_date,
            is_completed=False,
        )

    def to_dict(self) -> Dict[str, object]:
        """Convert the task into a JSON-safe dictionary."""
        return {
            "title": self.title,
            "time_of_day": self.time_of_day.strftime("%H:%M"),
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "owner_pet": self.owner_pet,
            "due_date": self.due_date.isoformat(),
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Task":
        """Create a Task from a dictionary previously produced by ``to_dict``."""
        return cls(
            title=str(data.get("title", "Untitled task")),
            time_of_day=_parse_time_string(str(data.get("time_of_day", "08:00"))),
            duration_minutes=int(data.get("duration_minutes", 15)),
            priority=str(data.get("priority", "medium")),
            frequency=str(data.get("frequency", "once")),
            owner_pet=str(data.get("owner_pet")) if data.get("owner_pet") is not None else None,
            due_date=date.fromisoformat(str(data.get("due_date", date.today().isoformat()))),
            is_completed=bool(data.get("is_completed", False)),
        )


@dataclass
class Pet:
    """Represents a pet owned by the owner."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(
        self,
        title: str,
        time_str: str,
        duration_minutes: int,
        priority: str = "medium",
        frequency: str = "once",
        due_date: Optional[date] = None,
    ) -> Task:
        """Create and append a new task for this pet."""
        if due_date is None:
            due_date = date.today()
        task = Task(
            title=title,
            time_of_day=_parse_time_string(time_str),
            duration_minutes=int(duration_minutes),
            priority=priority,
            frequency=frequency,
            owner_pet=self.name,
            due_date=due_date,
        )
        self.tasks.append(task)
        return task

    def get_tasks(self, include_completed: bool = False) -> List[Task]:
        """Return tasks for this pet."""
        if include_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.is_completed]

    def to_dict(self) -> Dict[str, object]:
        """Convert the pet into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Pet":
        """Create a Pet from a dictionary."""
        tasks_data = data.get("tasks", [])
        tasks = [Task.from_dict(task_data) for task_data in tasks_data] if isinstance(tasks_data, list) else []
        return cls(
            name=str(data.get("name", "Unnamed Pet")),
            species=str(data.get("species", "other")),
            tasks=tasks,
        )


@dataclass
class Owner:
    """Represents a pet owner who can manage multiple pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, name: str, species: str) -> Pet:
        """Create and add a new pet to the owner."""
        pet = Pet(name=name, species=species)
        self.pets.append(pet)
        return pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return a pet by name if it exists."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """Return all tasks across all pets."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks

    def to_dict(self) -> Dict[str, object]:
        """Convert the owner and nested pets/tasks into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    def save_to_json(self, filepath: str = DEFAULT_DATA_FILE) -> None:
        """Persist the owner, pets, and tasks into a JSON file."""
        target = Path(filepath)
        target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Owner":
        """Create an Owner from a dictionary."""
        pets_data = data.get("pets", [])
        pets = [Pet.from_dict(pet_data) for pet_data in pets_data] if isinstance(pets_data, list) else []
        return cls(
            name=str(data.get("name", "Jordan")),
            pets=pets,
        )

    @classmethod
    def load_from_json(cls, filepath: str = DEFAULT_DATA_FILE) -> "Owner":
        """Load owner data from JSON if it exists, otherwise return a blank owner."""
        target = Path(filepath)
        if not target.exists():
            return cls(name="Jordan")
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return cls(name="Jordan")
            return cls.from_dict(data)
        except Exception:
            return cls(name="Jordan")


class Scheduler:
    """The scheduling engine for PawPal+."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_tasks(self, tasks: Iterable[Task]) -> List[Task]:
        """Sort tasks by priority descending, then by time ascending."""
        return sorted(tasks, key=lambda task: (-task.priority_weight, task.time_of_day))

    def filter_tasks(
        self,
        tasks: Iterable[Task],
        *,
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        filtered: List[Task] = []
        for task in tasks:
            if pet_name is not None and task.owner_pet != pet_name:
                continue
            if status == "completed" and not task.is_completed:
                continue
            if status == "pending" and task.is_completed:
                continue
            filtered.append(task)
        return filtered

    def detect_conflicts(self, tasks: Iterable[Task]) -> List[str]:
        """Return warnings for tasks that share the exact same start time."""
        grouped: Dict[Tuple[date, time], List[Task]] = {}
        for task in tasks:
            grouped.setdefault((task.due_date, task.time_of_day), []).append(task)

        conflicts: List[str] = []
        for (due_date_value, time_value), group in grouped.items():
            if len(group) > 1:
                titles = ", ".join(f"{task.title} ({task.owner_pet})" for task in group)
                conflicts.append(
                    f"Conflict on {due_date_value.isoformat()} at {time_value.strftime('%H:%M')}: {titles}"
                )
        return conflicts

    def build_daily_plan(
        self,
        target_date: Optional[date] = None,
        *,
        include_completed: bool = False,
    ) -> Tuple[List[Task], List[str]]:
        """Build the ordered schedule for one date and return conflicts too."""
        if target_date is None:
            target_date = date.today()
        tasks = self.owner.get_all_tasks(include_completed=include_completed)
        tasks_for_day = [task for task in tasks if task.due_date == target_date]
        ordered = self.sort_tasks(tasks_for_day)
        conflicts = self.detect_conflicts(ordered)
        return ordered, conflicts

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and append the next recurring copy if needed."""
        new_task = task.mark_complete()
        if new_task is not None and new_task.owner_pet:
            pet = self.owner.get_pet(new_task.owner_pet)
            if pet is not None:
                pet.tasks.append(new_task)
        return new_task

    def explain_plan(self, tasks: List[Task], conflicts: List[str]) -> str:
        """Explain the ordering of a schedule in plain language."""
        if not tasks:
            return "No tasks scheduled for the selected date."

        lines = [
            "Tasks are ordered by priority (high → medium → low) and then by time.",
        ]
        for index, task in enumerate(tasks, start=1):
            lines.append(
                f"{index}. {task.title} for {task.owner_pet} at {task.time_of_day.strftime('%H:%M')} "
                f"(priority={task.priority}, time={task.time_of_day.strftime('%H:%M')})"
            )
        if conflicts:
            lines.append("")
            lines.append("Conflicts detected:")
            for conflict in conflicts:
                lines.append(f"- {conflict}")
        return "\n".join(lines)

    def find_next_available_slot(
        self,
        target_date: Optional[date] = None,
        duration_minutes: int = 30,
        day_start: str = "06:00",
        day_end: str = "22:00",
        step_minutes: int = 15,
    ) -> Optional[time]:
        """Find the next open time slot on a date using 15-minute steps.

        This optional extension looks at scheduled tasks on a day, treats each as a
        time interval using its duration, and returns the earliest available slot
        that fits the requested duration.
        """
        if target_date is None:
            target_date = date.today()

        start_minutes = _time_to_minutes(_parse_time_string(day_start))
        end_minutes = _time_to_minutes(_parse_time_string(day_end))
        if duration_minutes <= 0 or end_minutes - start_minutes < duration_minutes:
            return None

        day_tasks = [task for task in self.owner.get_all_tasks(include_completed=False) if task.due_date == target_date]
        intervals: List[Tuple[int, int]] = []
        for task in day_tasks:
            interval_start = _time_to_minutes(task.time_of_day)
            interval_end = interval_start + int(task.duration_minutes)
            intervals.append((interval_start, interval_end))
        intervals.sort()

        candidate = start_minutes
        while candidate + duration_minutes <= end_minutes:
            candidate_end = candidate + duration_minutes
            overlaps = False
            for interval_start, interval_end in intervals:
                if candidate < interval_end and candidate_end > interval_start:
                    overlaps = True
                    break
            if not overlaps:
                return _minutes_to_time(candidate)
            candidate += step_minutes
        return None


__all__ = ["Task", "Pet", "Owner", "Scheduler", "DEFAULT_DATA_FILE"]
