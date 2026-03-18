"""CLI demo for PawPal+ using tabulate for cleaner formatting."""

from datetime import date

from tabulate import tabulate

from pawpal_system import Owner, Scheduler


def main() -> None:
    owner = Owner(name="Jordan")
    mochi = owner.add_pet("Mochi", "dog")
    luna = owner.add_pet("Luna", "cat")

    mochi.add_task("Morning walk", "07:00", 30, priority="high", frequency="daily")
    mochi.add_task("Breakfast", "08:00", 10, priority="high")
    luna.add_task("Play session", "08:00", 15, priority="medium")
    luna.add_task("Dinner", "18:00", 10, priority="medium", frequency="daily")

    scheduler = Scheduler(owner)
    ordered, conflicts = scheduler.build_daily_plan(date.today())

    table = [
        [task.owner_pet, task.title, task.time_of_day.strftime("%H:%M"), task.priority, task.duration_minutes, task.frequency]
        for task in ordered
    ]
    print("Today's schedule\n")
    print(tabulate(table, headers=["Pet", "Task", "Time", "Priority", "Duration", "Frequency"], tablefmt="github"))

    if conflicts:
        print("\nConflicts")
        for conflict in conflicts:
            print(f"- {conflict}")

    print("\nExplanation\n")
    print(scheduler.explain_plan(ordered, conflicts))


if __name__ == "__main__":
    main()
