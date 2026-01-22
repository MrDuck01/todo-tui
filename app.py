
from prompt_toolkit import Application
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout import ScrollOffsets
from prompt_toolkit.layout.containers import DynamicContainer
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.widgets import TextArea
import asyncio

from core.task import Task
from storage import sqlite as storage
from core.status import Status, ORDER, STYLES
from ui.status_picker import pick_status_async
from ui.helper import get_task_counts
from ui.helper import get_footer_text
from datetime import datetime

# Intial Setup

# session = PromptSession()

# Functions

def render_tasks():
    if not tasks:
        return "No tasks\n"
    
    lines = []
    for i, task in enumerate(tasks):
        prefix = "> " if i == current_index else "  "
        lines.append(f"{prefix}{i + 1}. {task}")

    return "\n".join(lines)

def get_task_text():
    lines = []

    if not tasks:
        return[("class:text", "No tasks\n")]
    
    for i, task in enumerate(tasks):
        if i == current_index:
            style = "class:selected"
        else:
            style = STYLES.get(task.status, "class:text")
        
        lines.append((style, f"{i + 1}. {task}\n"))

    return lines

def get_header_text():
    counts = get_task_counts(tasks)

    return [
        ("class:header", " Tasks "),
        ("class:count", f"Total: {counts['total'] } "),
        ("class:active", f"Active: {counts[Status.ACTIVE]} "),
        ("class:progress", f"In Progress: {counts[Status.IN_PROGRESS]} "),
        ("class:hold", f"On Hold: {counts[Status.HOLD]} "),
        ("class:cancelled", f"Cancelled: {counts[Status.CANCELLED]} "),
        ("", "\n"),
        ("class:seperator", "-" * 60 + "\n"),
    ]

# Window Setup

header_control = FormattedTextControl(get_header_text)
header_window = Window(
    content = header_control,
    height = Dimension.exact(3),
    dont_extend_height=True,
)

footer_control = FormattedTextControl(get_footer_text)
footer_window = Window(
    content = footer_control,
    height = Dimension.exact(1),
    dont_extend_height=True,
)

task_control = FormattedTextControl(
    text = get_task_text,
    focusable=False,
    show_cursor=False
)

task_window = Window(
    content=task_control,
    always_hide_cursor=True,
    scroll_offsets=ScrollOffsets(top=1, bottom=1)
)

layout = Layout(
    HSplit([
        header_window,
        task_window,
        footer_window,
    ])
)

# Key Bindings

kb = KeyBindings()

@kb.add("up")
def move_up(event):
    global current_index
    if tasks:
        current_index = max(0, current_index - 1)
        event.app.invalidate()

@kb.add("down")
def move_down(event):
    global current_index
    if tasks:
        current_index = min(len(tasks) -1, current_index + 1)
        event.app.invalidate() 

@kb.add("s")
def change_status(event):
    if not tasks:
        return
    
    task = tasks[current_index]

    async def _change():
        new_status = await pick_status_async(task.status)
        if new_status is None:
            return

        task.status = new_status
        task.last_updated = datetime.now()

        if new_status == Status.CANCELLED:
            task.completed_at = task.last_updated
        else:
            task.completed_at = None

        storage.update_task_status(
            task.id,
            task.status.value,
            task.last_updated,
            task.completed_at
        )

        event.app.invalidate()

    asyncio.create_task(_change())

@kb.adqd("a")
def add_task(event):
    app = event.app
    
    async def _add():
        def ask():
            return prompt("New task: ")
    
        name = await run_in_terminal(ask)

        if not name:
            return
        name = name.strip()
        if not name:
            return

        task = Task(name)
        storage.insert_task(task)
        tasks.append(task)
        app.invalidate()
    asyncio.create_task(_add())


@kb.add("d")
def delete_task(event):
    global current_index
    if not tasks:
        return

    task = tasks[current_index]
    storage.delete_task(task)
    tasks.pop(current_index)
    current_index = max(0, current_index - 1)

    event.app.invalidate()

@kb.add("q")
def quit_app(event):
    event.app.exit()

# Initialise storage
storage.init_db()
tasks = storage.get_all_tasks()
current_index = 0


# Style

style = Style.from_dict({
    "header": "bold",
    "seperator": "fg:#444444",
    
    "count": "fg:white",
    "active": "fg:green",
    "progress": "fg:yellow",
    "hold": "fg:cyan",
    "cancelled": "fg:red",

    "text": "",
    "selected": "reverse",
})

app = Application(
    layout = layout,
    key_bindings = kb,
    style = style,
    full_screen = True
)

app.run()