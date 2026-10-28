"""To-Do list skill for Mini-Alexa to add, list, and remove tasks stored in todo.json."""

import json
import os
import re

TODO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "todo.json")

def _load_tasks() -> list:
    """Load tasks from todo.json file."""
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_tasks(tasks: list):
    """Save tasks to todo.json file."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def manage_todo(command: str) -> str:
    """
    Manage to-do list: add, list, and remove tasks.
    Persists data in todo.json.
    """
    if not command:
        return "You can ask me to add a task, list your tasks, or remove a task."

    cmd = command.strip().lower()
    tasks = _load_tasks()

    # 1. ADD task (check first to handle 'add ... to my todo list')
    if any(k in cmd for k in ["add", "put", "insert", "new task"]):
        task = re.sub(
            r"^(add\s+task|add|put|insert|new\s+task)\s+",
            "",
            cmd,
            flags=re.IGNORECASE,
        )
        task = re.sub(
            r"\b(to\s+my\s+todo\s+list|to\s+todo\s+list|to\s+my\s+todo|to\s+todo|in\s+my\s+todo|in\s+todo)\b",
            "",
            task,
            flags=re.IGNORECASE,
        ).strip()

        if not task:
            return "What task would you like to add to your to-do list?"

        tasks.append(task)
        _save_tasks(tasks)
        return f"Added '{task}' to your to-do list."

    # 2. REMOVE / DELETE task
    elif any(k in cmd for k in ["remove", "delete", "clear", "done with", "completed"]):
        if not tasks:
            return "Your to-do list is already empty."

        # Check for clearing entire list
        if "clear all" in cmd or "clear todo" in cmd:
            _save_tasks([])
            return "I have cleared all tasks from your to-do list."

        # Check if user specified a task number e.g. "remove task 1"
        num_match = re.search(r"\b(?:task|number|#)?\s*(\d+)\b", cmd)
        if num_match:
            idx = int(num_match.group(1)) - 1
            if 0 <= idx < len(tasks):
                removed_item = tasks.pop(idx)
                _save_tasks(tasks)
                return f"Removed '{removed_item}' from your to-do list."
            else:
                return f"Task number {idx + 1} does not exist. You have {len(tasks)} tasks."

        # Match task by name
        target_task = re.sub(
            r"^(remove\s+task|remove|delete\s+task|delete|done\s+with)\s+",
            "",
            cmd,
            flags=re.IGNORECASE,
        )
        target_task = re.sub(
            r"\b(from\s+my\s+todo\s+list|from\s+todo\s+list|from\s+my\s+todo|from\s+todo)\b",
            "",
            target_task,
            flags=re.IGNORECASE,
        ).strip()

        if not target_task:
            return "Which task would you like to remove?"

        # Search for matching task
        matched_idx = -1
        for i, t in enumerate(tasks):
            if target_task in t.lower() or t.lower() in target_task:
                matched_idx = i
                break

        if matched_idx != -1:
            removed_item = tasks.pop(matched_idx)
            _save_tasks(tasks)
            return f"Removed '{removed_item}' from your to-do list."
        else:
            return f"I couldn't find '{target_task}' in your to-do list."

    # 3. LIST tasks
    elif any(k in cmd for k in ["list", "show", "what is on", "what's on", "read", "view", "tasks", "todo"]):
        if not tasks:
            return "Your to-do list is empty."

        task_list_str = ", ".join(f"{i + 1}. {task}" for i, task in enumerate(tasks))
        count = len(tasks)
        plural = "task" if count == 1 else "tasks"
        return f"You have {count} {plural} on your to-do list: {task_list_str}."

    else:
        return "You can say: add buy milk to my todo, list my todo, or remove task 1."
