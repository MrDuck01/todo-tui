
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.reactive import reactive
from textual.screen import Screen
from textual import log
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from datetime import datetime
import logging 
from enum import Enum, auto


from ui.categories import CategoryPicker
from ui.status_picker import StatusPicker
from ui.add_task import AddTaskScreen
from core.task import Task
from core.status import Status, ORDER, STYLES
from storage import sqlite as storage

import asyncio

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Intial Setup
class SortKey(Enum):
    NAME = auto()
    CATEGORY = auto()
    STATUS = auto()
    CREATED = auto()
    UPDATED = auto()


class TaskItem(ListItem):
    def __init__(self, model: Task):
        assert isinstance(model, Task), type(model)
        self.model = model
        super().__init__(
            Horizontal(
                Label(model.name, classes="col-name"),
                Label("|", classes="col-sep"),
                Label(model.category, classes="col-category"),
                Label("|", classes="col-sep"),
                Label(model.status.value, classes = "col-status"),
                Label("|", classes="col-sep"),
                Label(model.created_at.strftime("%Y-%m-%d"), classes="col-created"),
                Label("|", classes="col-sep"),
                Label(model.last_updated.strftime("%Y-%m-%d %H:%M"), classes="col-updated"),
            )
        )
    
    def refresh_row(self):
        self.query_one(".col-status", Label).update(self.model.status.value)
        self.query_one(".col-updated", Label).update(
            self.model.last_updated.strftime("%Y-%m-%d %H:%M")
        )
        

    def update_model(self, model: Task):
        self.model = model
        self.query_one(Label).update(str(model))

class TodoApp(App):

    filter_status: Status | None = None 
    filter_category: str | None = None
    filter_category_include: bool = True
    sort_key: SortKey | None = None
    sort_reverse: bool = False

    CSS_PATH = "app.css"
    BINDINGS = [
        Binding("a", "add_task", "Add"),
        Binding("s", "toggle_status", "Toggle"),
        Binding("d", "action_delete_task", "Delete"),
        Binding("q", "quit", "Quit"),
        Binding("b", "filter_screen", "Filter"),
        Binding("f", "filter_active", "Active", priority=True),
        Binding("i", "filter_in_progress", "In Progress", priority=True),
        Binding("h", "filter_hold", "On Hold", priority=True),
        Binding("c", "filter_cancelled", "Cancelled", priority=True),
        Binding("x", "clear_filter", "All", priority=True),
        Binding("1", "sort_name", "Sort Name"),
        Binding("2", "sort_category", "Sort Category"),
        Binding("3", "sort_status", "Sort Status"),
        Binding("4", "sort_created", "Sort Created"),
        Binding("5", "sort_updated", "Sort Updated"),
        Binding("r", "reverse_sort", "Reverse")
    ]

    def update_summary(self):
        total = len(self.tasks)
        active = sum(1 for t in self.tasks if t.status == Status.ACTIVE)
        progress = sum(1 for t in self.tasks if t.status == Status.IN_PROGRESS)
        hold = sum(1 for t in self.tasks if t.status == Status.HOLD)
        
        logging.debug(f"Update Summary -- Total {total}")
        logging.debug(f"Update Summary -- Active {active}")
        logging.debug(f"Update Summary -- Progress {progress}")
        logging.debug(f"Update Summary -- Hold {hold}")
        
        text = (
            f"Total: {total} | "
            f"Active: {active} | "
            f"In Progress: {progress} | "
            f"On Hold: {hold}"
        )

        self.query_one("#summary", Label).update(text)

    def watch_summary(self, value):
        self.query_one("#summary", Label).update(value)
        def action_add_task(self):
         self.push_screen(AddTaskScreen(), self._on_task_added)

    def on_mount(self):
        storage.init_db()
        self.tasks = storage.get_all_tasks()
        self.refresh_list()
        self.update_summary()

# Display and Sorting

    def compose(self) -> ComposeResult:
        yield Header(
            Label(self._sort_label("Task", SortKey.NAME), classes= "col-name header")
        )

        yield Vertical(
            Horizontal(
                Label("Tasks", id="summary"),
                id="summary-bar"
            ),
            Horizontal(
                Label("Task", classes="col-name header"),
                Label("|", classes="col-sep"),
                Label("Category", classes="col-category header"),
                Label("|", classes="col-sep"),
                Label("Status", classes="col-status header"),
                Label("|", classes="col-sep"),
                Label("Created", classes="col-created header"),
                Label("|", classes="col-sep"),
                Label("Updated", classes="col-updated header"),
                classes="table-header",
            ),
            ListView(id="tasks"),
            id="main",
        )
        yield Footer()

    def _sort_label(self, text: str, key: SortKey) -> str:
        if self.sort_key != key:
            return text
        return f"{text} {'↓' if self.sort_reverse else '↑'}"

    def refresh_list(self):
        logging.debug(f"get_visible_tasks attr: {self.get_visible_tasks}")
        tasks = self.get_visible_tasks()
        logging.debug(f"get_visible_tasks() returned: {tasks!r}")
        logging.debug(f"type: {type(tasks)}")

        list_view = self.query_one("#tasks", ListView)
        list_view.clear()

        for task in tasks:
            list_view.append(TaskItem(task))

    def get_visible_tasks(self) -> list[Task]:
        tasks = list(self.tasks)

        logging.debug(f"get_visible_tasks: filter_status={self.filter_status}, filter_category={self.filter_category}, sort_key={self.sort_key}, sort_reverse={self.sort_reverse}")

        # filter
        tasks = [
            t for t in tasks
                if (
                    (self.filter_status is None or t.status == self.filter_status)
                    and self._category_matches(t)
                )
          ]
          
        # sort
        if self.sort_key is not None:
            tasks.sort(
                key = self._sort_key_func,
                reverse = self.sort_reverse
            )

        return tasks
    
    def _category_matches(self, task) -> bool:
        if self.filter_category is None:
            return True 
        if self.filter_category_include:
            return task.category == self.filter_category
        else:
            return task.category != self.filter_category
        

    def _sort_key_func(self, task: Task):
        match self.sort_key:
            case SortKey.NAME:
                return task.name.lower()
            case SortKey.CATEGORY:
                return task.category.lower()
            case SortKey.STATUS:
                return ORDER.index(task.status)
            case SortKey.CREATED:
                return task.created_at
            case SortKey.UPDATED:
                return task.last_updated

    def _set_sort(self, key: SortKey):
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = False
        
        self.refresh_list()
    
# Actions

    def action_sort_name(self):
        self._set_sort(SortKey.NAME)
    
    def action_sort_category(self):
        self._set_sort(SortKey.CATEGORY)

    def action_sort_status(self):
        self._set_sort(SortKey.STATUS)

    def action_sort_created(self):
        self._set_sort(SortKey.CREATED)
    
    def action_sort_updated(self):
        self._set_sort(SortKey.UPDATED)
    
    def action_reverse_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.refresh_list()

    def action_add_task(self):
        self.push_screen(AddTaskScreen(), self._on_task_added)
    
    def _on_task_added(self, task: Task | None):
        if task is None:
            return
        logging.debug(f"Add Task event: {task.name} | {task.category}")
        storage.insert_task(task)
        self.tasks.append(task)
        self.refresh_list()
        self.update_summary()
    
    def action_filter_screen(self):
        self.push_screen(CategoryPicker(), self._on_category_selected)

    def _on_category_selected(self, result: tuple[str, bool] | None):
        if result is None:
            return
        
        category, include = result
        logging.debug(f"Selected category: {category}, include: {include}")
        self.filter_category = category
        self.filter_category_include = include

        self.refresh_list()

    def action_toggle_status(self):
        list_view = self.query_one(ListView)
        item = list_view.highlighted_child
        logging.debug(f"action_toggle_status: item type (inital) {type(item)}")
        logging.debug(f"action_toggle_status: item.task type (inital) {type(item.task)}")
        if not item:
            return

        self.push_screen(
            StatusPicker(),
            lambda status: self._apply_status(item, status)
        )
        
    def _apply_status(self, item, status):
        logging.debug(f"_apply_status: item type (initial) {type(item)}")
        logging.debug(f"_apply_status: item.model type (initial) {type(item.model)}")

        if status is None:
            return

        item.model.set_status(status)
        dt = datetime.now()
        if status == Status.COMPLETED:
            cd = dt
        else:
            cd = None
        storage.update_task_status(item.model, status, dt, cd)
        item.refresh_row()
        self.update_summary()

    def action_change_status(self):
        self.push_screen(StatusPicker)

    def action_delete_task(self):
        list_view = self.query_one("#tasks", ListView)
        if list_view.index is None:
            return
        task = self.tasks.pop(list_view.index)
        storage.delete_task(task.id)
        self.refresh_list()

    def action_filter_active(self):
        logging.debug(f"Filter applied f a ")
        self.filter_status = Status.ACTIVE
        self.refresh_list()

    def action_filter_in_progress(self):
        logging.debug(f"Filter applied f i ")
        self.filter_status = Status.IN_PROGRESS
        self.refresh_list()

    def action_filter_hold(self):
        logging.debug(f"Filter applied f h ")
        self.filter_status = Status.HOLD
        self.refresh_list()

    def action_filter_cancelled(self):
        logging.debug(f"Filter applied f c ")
        self.filter_status = Status.CANCELLED
        self.refresh_list()

    def action_clear_filter(self):
        logging.debug(f"Filter applied f x ")
        self.filter_status = None
        self.filter_category = None
        self.refresh_list()


if __name__ == "__main__":
    TodoApp().run()
