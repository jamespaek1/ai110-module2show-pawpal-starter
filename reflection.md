# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

My initial UML design focused on four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

The `Owner` class was responsible for managing multiple pets. The `Pet` class stored information about one pet and its list of tasks. The `Task` class represented one care activity such as a walk, feeding, grooming task, or medication. The `Scheduler` class acted as the main logic layer that collected tasks, sorted them, filtered them, and produced a daily schedule.

I chose these classes because they matched the real-world structure of the problem. An owner can have many pets, each pet can have many tasks, and the scheduler needs to organize tasks across all pets.

### b. Design changes

Yes, my design changed during implementation.

One important change was adding recurrence logic directly to tasks. At first, I planned for the scheduler to handle all recurring behavior. Later, I realized it made more sense for each task to know how to create its own next occurrence when marked complete. That made the design cleaner and reduced extra logic in the scheduler.

Another change was adding conflict detection. My original design focused mostly on sorting, but I later added a lightweight method that checks for exact-time conflicts so the app could warn the user when two tasks are scheduled at the same time.

For the optional extension work, I also added JSON serialization methods to `Task`, `Pet`, and `Owner`, plus `save_to_json()` and `load_from_json()` on the owner. I added a separate smart feature in the scheduler called `find_next_available_slot()` so I could go beyond the base requirements without making the main schedule builder too complicated.

---

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

My scheduler considers these main constraints:

- selected date
- task priority
- task time
- completion status
- pet association

I decided priority and time mattered most because the project scenario described a busy pet owner who needs help deciding what to do first. High-priority tasks like feeding or medication should come before lower-priority tasks, and tasks with the same priority should still follow a logical time order.

For the optional slot suggestion feature, I also considered task durations because the scheduler needs those to find a real open window.

### b. Tradeoffs

One tradeoff my scheduler makes is that the main schedule only detects conflicts when two tasks have the exact same start time. It does not yet detect every overlapping duration conflict in the core schedule builder.

I think this tradeoff is reasonable because it keeps the main logic simple, readable, and easy to test. At the same time, I still added one more advanced algorithmic feature through `find_next_available_slot()`, which does use duration-based intervals. That let me add more intelligence without overcomplicating the base design.

---

## 3. AI Collaboration

### a. How you used AI

I used AI tools to help brainstorm class structure, improve method design, and think through testing. AI was especially useful when I needed help organizing the problem into smaller pieces, like deciding what responsibilities belonged in `Task` versus `Scheduler`.

The most helpful prompts were questions like:
- What classes should a pet care scheduling app have?
- How should I sort tasks by priority and then by time?
- What are important tests for recurrence and scheduling?
- How can I connect backend classes to a Streamlit UI?
- How should I serialize nested pet/task objects into JSON cleanly?
- What is a simple way to search for the next available slot in 15-minute steps?

AI also helped me improve code structure and think about edge cases.

### b. Judgment and verification

One example of not accepting an AI suggestion as-is was conflict detection. A more advanced version would have checked overlapping durations everywhere, but I decided not to use that version in the main schedule because it would make the project more complicated than necessary for this assignment.

I evaluated the suggestion by thinking about the project requirements and the tradeoff between complexity and clarity. I kept the simpler exact-time version for the base schedule and used a separate next-slot algorithm for the optional extension.

---

## 4. Testing and Verification

### a. What you tested

I tested these main behaviors:

- adding a task to a pet
- marking a recurring task complete and creating the next occurrence
- ordering tasks by priority and then time
- exact-time conflict detection
- saving owner data to JSON and loading it back
- finding the next available slot on a partially filled day

These tests were important because they cover both the base assignment logic and the optional extensions. If these parts fail, then the schedule shown in the UI would not be reliable.

### b. Confidence

I am fairly confident that my scheduler works correctly for common use cases. My automated tests passed, and the Streamlit app produced schedules that matched the expected order.

If I had more time, I would test these additional edge cases:

- overlapping-duration conflicts in the main scheduler
- corrupted or partially missing JSON data
- pets with no tasks
- repeated pet names
- marking tasks complete inside the UI
- loading a much larger saved dataset

---

## 5. Reflection

### a. What went well

The part I am most satisfied with is the separation between the backend logic and the UI. Building the scheduler in `pawpal_system.py` first made it easier to test the core logic before connecting it to Streamlit.

I am also satisfied that the app now shows a real schedule and explanation instead of placeholder text, and that it now saves and reloads data between runs.

### b. What you would improve

If I had another iteration, I would improve the app by adding task editing, deleting, persistence controls in the UI, and stronger conflict detection. I would also add filters, better styling, and the ability to mark tasks complete directly from the app.

### c. Key takeaway

One important thing I learned is that being the lead architect means deciding what to keep simple and what to improve later. AI can generate ideas quickly, but I still had to make decisions about design quality, readability, and what was realistic for the assignment.

I also learned that testing the backend first makes it much easier to debug the UI later.

---

## 6. Prompt Comparison (Optional Extension)

I could not run a true side-by-side comparison with a second external model in this environment, so I do not want to pretend I completed a fully validated multi-model experiment. However, I can still describe the comparison framework I would use.

If I compared a weekly recurrence or rescheduling prompt across two models, I would judge them on:

- modularity
- readability
- how many assumptions they make
- how easy the output is to test
- whether the code keeps logic in the right class

Based on the style of responses I found most useful during this project, the more Pythonic solution is the one that keeps recurrence logic close to the `Task` model and keeps the `Scheduler` focused on coordination instead of doing everything itself. That was the design direction I chose because it felt easier to maintain and explain.

So while I cannot honestly claim a full OpenAI-vs-Claude-or-Gemini experiment here, I can say that I now understand what I would compare and why maintainability matters more than simply generating more code.
