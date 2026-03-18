from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from pawpal_system import DEFAULT_DATA_FILE, Owner, Scheduler

DATA_FILE = Path(__file__).with_name(DEFAULT_DATA_FILE)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown("Plan your pet care tasks with priority-based scheduling, persistence, and smart suggestions.")


# ---------------------------
# Helpers
# ---------------------------
def load_owner() -> Owner:
    return Owner.load_from_json(str(DATA_FILE))


def refresh_scheduler() -> None:
    st.session_state.scheduler = Scheduler(st.session_state.owner)


def save_data() -> None:
    st.session_state.owner.save_to_json(str(DATA_FILE))


def priority_label(priority: str) -> str:
    mapping = {
        "high": "🔴 High",
        "medium": "🟡 Medium",
        "low": "🟢 Low",
    }
    return mapping.get(priority.lower(), priority.title())


def status_label(is_completed: bool) -> str:
    return "✅ Done" if is_completed else "🕒 Pending"


def style_priority(value: str) -> str:
    if value.startswith("🔴"):
        return "background-color: #fde2e1"
    if value.startswith("🟡"):
        return "background-color: #fff6d6"
    if value.startswith("🟢"):
        return "background-color: #e5f6e8"
    return ""


def style_status(value: str) -> str:
    if value.startswith("✅"):
        return "background-color: #e5f6e8"
    if value.startswith("🕒"):
        return "background-color: #eef1f5"
    return ""


# ---------------------------
# Session state setup
# ---------------------------
if "owner" not in st.session_state:
    st.session_state.owner = load_owner()

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.caption(f"Autosaves to: {DATA_FILE.name}")

# ---------------------------
# Owner + Pet info
# ---------------------------
st.subheader("Owner and Pet Info")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

pet_name_input = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

col_a, col_b, col_c = st.columns([1, 1, 1.2])
with col_a:
    if st.button("Add pet"):
        existing_pet = st.session_state.owner.get_pet(pet_name_input)
        if existing_pet is None:
            st.session_state.owner.add_pet(pet_name_input, species)
            refresh_scheduler()
            save_data()
            st.success(f"Added pet: {pet_name_input}")
        else:
            st.info(f"{pet_name_input} already exists.")
with col_b:
    if st.button("Save now"):
        save_data()
        st.success("Saved to data.json")
with col_c:
    if DATA_FILE.exists() and st.button("Reload saved data"):
        st.session_state.owner = load_owner()
        refresh_scheduler()
        st.success("Reloaded saved data.")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.write(", ".join([pet.name for pet in st.session_state.owner.pets]))
else:
    st.caption("No pets added yet.")

st.divider()

# ---------------------------
# Add task
# ---------------------------
st.subheader("Add Task")

existing_pet_names = [pet.name for pet in st.session_state.owner.pets]
if existing_pet_names:
    selected_pet_name = st.selectbox("Choose a pet", existing_pet_names, index=0)
else:
    selected_pet_name = pet_name_input
    st.info("Add a pet first or use the pet name box above.")

col1, col2 = st.columns(2)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.time_input("Task time")

col3, col4, col5, col6 = st.columns(4)
with col3:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)
with col6:
    task_date = st.date_input("Task date", value=date.today())

slot_col1, slot_col2 = st.columns([1, 1.2])
with slot_col1:
    if st.button("Suggest next available slot"):
        suggested = st.session_state.scheduler.find_next_available_slot(task_date, int(duration))
        if suggested is None:
            st.warning("No open slot found in the default day window.")
        else:
            st.success(f"Suggested next open slot: {suggested.strftime('%H:%M')}")
with slot_col2:
    st.caption("This optional feature scans the day in 15-minute steps to find the next open window.")

if st.button("Add task"):
    pet = st.session_state.owner.get_pet(selected_pet_name)
    if pet is None:
        pet = st.session_state.owner.add_pet(selected_pet_name, species)

    pet.add_task(
        title=task_title.strip(),
        time_str=task_time.strftime("%H:%M"),
        duration_minutes=int(duration),
        priority=priority,
        frequency=frequency,
        due_date=task_date,
    )
    refresh_scheduler()
    save_data()
    st.success(f"Added task '{task_title}' for {selected_pet_name}.")

# ---------------------------
# Show all tasks
# ---------------------------
all_tasks = st.session_state.owner.get_all_tasks(include_completed=True)
if all_tasks:
    st.markdown("### Current Tasks")
    task_rows = []
    for task in all_tasks:
        task_rows.append(
            {
                "Pet": task.owner_pet,
                "Task": task.title,
                "Date": task.due_date.isoformat(),
                "Time": task.time_of_day.strftime("%H:%M"),
                "Duration": f"{task.duration_minutes} min",
                "Priority": priority_label(task.priority),
                "Frequency": task.frequency,
                "Completed": status_label(task.is_completed),
            }
        )
    tasks_df = pd.DataFrame(task_rows)
    styled_tasks_df = tasks_df.style.map(style_priority, subset=["Priority"]).map(style_status, subset=["Completed"])
    st.dataframe(styled_tasks_df, use_container_width=True, hide_index=True)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------
# Build schedule
# ---------------------------
st.subheader("Build Schedule")
selected_date = st.date_input("Schedule date", value=date.today(), key="schedule_date")

if st.button("Generate schedule"):
    ordered, conflicts = st.session_state.scheduler.build_daily_plan(selected_date)

    if ordered:
        st.markdown(f"### Schedule for Selected Date: {selected_date}")
        schedule_rows = []
        for task in ordered:
            schedule_rows.append(
                {
                    "Pet": task.owner_pet,
                    "Task": task.title,
                    "Time": task.time_of_day.strftime("%H:%M"),
                    "Priority": priority_label(task.priority),
                    "Duration": f"{task.duration_minutes} min",
                    "Frequency": task.frequency,
                }
            )
        schedule_df = pd.DataFrame(schedule_rows)
        styled_schedule_df = schedule_df.style.map(style_priority, subset=["Priority"])
        st.dataframe(styled_schedule_df, use_container_width=True, hide_index=True)

        explanation = st.session_state.scheduler.explain_plan(ordered, conflicts)
        st.markdown("### Explanation")
        st.text(explanation)
    else:
        st.warning("No tasks scheduled for that date.")

    if conflicts:
        st.markdown("### Conflict Warnings")
        for conflict in conflicts:
            st.warning(conflict)
