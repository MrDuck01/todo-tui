
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.reactive import reactive
from textual.screen import Screen
from textual import log
from textual.containers import Vertical, Horizontal
from datetime import datetime

from ui.status_picker import StatusPicker
from ui.add_task import AddTaskScreen

import logging 

from core.task import Task
from core.status import Status, ORDER, STYLES
from storage import sqlite as storage

import asyncio

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Intial Setup

class TaskItem(ListItem):
    def __init__(self, model: Task):
        assert isinstance(model, Task), type(model)
        self.model = model
        super().__init__(
            Horizontal(
                Label(model.name, classes="col-name"),
                Label("|", classes="col-sep"),
                Label(model.status.value, classes = "col-status"),
                Label("|", classes="col-sep"),
                Label(model.create_at.strftime("%Y-%m-%d"), classes="col-created"),
                Label("|", classes="col-sep"),
                Label(model.last_updated.strftime("%Y-%m-%d %H:%M"), classes="col-updated"),
            )
        )
    
    def refresh_row(self):
        labels = self.query(Label)
        labels[1].update(self.model.status.value)
        labels[3].update(self.model.last_updated.strftime("%Y-%m-%d"))

    def update_model(self, model: Task):
        self.model = model
        self.query_one(Label).update(str(model))

    
    @property
    def task(self):
        return self._task
    
    @task.setter
    def task(self, value: Task):
        self._task = value
        self.label.update(str(value))

class TodoApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [
        ("a", "add_task", "Add"),
        ("s", "toggle_status", "Toggle"),
        ("d", "action_delete_task", "Delete"),
        ("q", "quit", "Quit")
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
    

    def compose(self) -> ComposeResult:
        yield Header()

        yield Vertical(
            Horizontal(
                Label("Tasks", id="summary"),
                id="summary-bar"
            ),
            Horizontal(
                Label("Task", classes="col-name header"),
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


    def on_mount(self):
        storage.init_db()
        self.tasks = storage.get_all_tasks()
        self.refresh_list()
        self.update_summary()


    def refresh_list(self):
        list_view = self.query_one("#tasks", ListView)
        list_view.clear()
        for task in self.tasks:
            logging.debug(f"refresh_list (build tasks) {task.name} {type(task)}")
            list_view.append(TaskItem(task))

    
    def action_add_task(self):
        self.push_screen(AddTaskScreen(), self._on_task_added)


    def _on_task_added(self, task: Task | None):
        if task is None:
            return

        storage.insert_task(task)

    
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
        
        #assert isinstance(item.task, Task)

        item.model.set_status(status)
        dt = datetime.now()
        if status == Status.COMPLETED:
            cd = dt
        else:
            cd = None
        storage.update_task_status(item.model, status, dt, cd)
        item.refresh_row()

    def action_change_status(self):
        self.push_screen(StatusPicker)

    def action_delete_task(self):
        list_view = self.query_one("#tasks", ListView)
        if list_view.index is None:
            return
        task = self.tasks.pop(list_view.index)
        storage.delete_task(task.id)
        self.refresh_list()

if __name__ == "__main__":
    TodoApp().run()
