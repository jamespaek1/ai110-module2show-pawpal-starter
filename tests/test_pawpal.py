"""Unit tests for the PawPal+ system."""

from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pawpal_system import Owner, Scheduler


def test_task_completion_creates_recurring_copy() -> None:
    owner = Owner("Test")
    pet = owner.add_pet("Buddy", "dog")
    task = pet.add_task("Daily walk", "10:00", 30, priority="medium", frequency="daily")
    scheduler = Scheduler(owner)

    new_task = scheduler.mark_task_complete(task)

    assert task.is_completed is True
    assert new_task is not None
    assert new_task.owner_pet == task.owner_pet
    assert new_task.due_date == date.today() + timedelta(days=1)
    assert new_task.is_completed is False
    assert len(pet.get_tasks(include_completed=True)) == 2


def test_add_task_increases_task_count() -> None:
    owner = Owner("Alex")
    pet = owner.add_pet("Whiskers", "cat")

    assert len(pet.get_tasks()) == 0
    pet.add_task("Feed", "08:00", 5)
    assert len(pet.get_tasks()) == 1
    pet.add_task("Play", "10:00", 15)
    assert len(pet.get_tasks()) == 2


def test_scheduler_sorts_by_priority_and_time() -> None:
    owner = Owner("Jordan")
    pet = owner.add_pet("Mochi", "dog")
    pet.add_task("Low priority later", "18:00", 10, priority="low")
    pet.add_task("High priority later", "19:00", 10, priority="high")
    pet.add_task("High priority early", "07:00", 10, priority="high")
    pet.add_task("Medium priority", "08:00", 10, priority="medium")
    scheduler = Scheduler(owner)

    ordered, _ = scheduler.build_daily_plan(date.today())
    ordered_titles = [task.title for task in ordered]

    assert ordered_titles[:2] == ["High priority early", "High priority later"]
    assert ordered_titles[2] == "Medium priority"
    assert ordered_titles[3] == "Low priority later"


def test_detect_conflict_for_same_time() -> None:
    owner = Owner("Jordan")
    pet = owner.add_pet("Mochi", "dog")
    pet.add_task("Walk", "09:00", 20, priority="high")
    pet.add_task("Breakfast", "09:00", 10, priority="high")
    scheduler = Scheduler(owner)

    _, conflicts = scheduler.build_daily_plan(date.today())

    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_save_and_load_json_round_trip(tmp_path: Path) -> None:
    filepath = tmp_path / "data.json"
    owner = Owner("Jordan")
    pet = owner.add_pet("Blueberry", "dog")
    pet.add_task("Park", "14:45", 30, priority="medium", frequency="daily")

    owner.save_to_json(str(filepath))
    loaded = Owner.load_from_json(str(filepath))

    assert loaded.name == "Jordan"
    assert len(loaded.pets) == 1
    assert loaded.pets[0].name == "Blueberry"
    assert loaded.pets[0].tasks[0].title == "Park"
    assert loaded.pets[0].tasks[0].frequency == "daily"


def test_find_next_available_slot() -> None:
    owner = Owner("Jordan")
    pet = owner.add_pet("Blueberry", "dog")
    pet.add_task("Walk", "06:00", 30, priority="high")
    pet.add_task("Breakfast", "07:00", 30, priority="medium")
    scheduler = Scheduler(owner)

    slot = scheduler.find_next_available_slot(date.today(), duration_minutes=30, day_start="06:00", day_end="08:00")

    assert slot is not None
    assert slot.strftime("%H:%M") == "06:30"
