from textual.screen import ModalScreen
from textual.widgets import Input, Button, ListView, ListItem, Label
from textual.containers import Vertical

from core.task import Task
from storage import sqlite as storage

class AddTaskScreen(ModalScreen[Task | None]):
    def compose(self):

        categorys = storage.get_categorys()

        yield Vertical(
            Input(placeholder = "Task name", id="name"),
            Input(placeholder = "Category", id="category"),
            ListView(
                *[ListItem(Label(category)) for category in categorys],
                id="categorys"
            ),
            Button("Add", id="add"),
            Button("Cancel", id="cancel"),
        )


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add":
            name = self.query_one("#name", Input).value.strip()
            category = self.query_one("#category", Input).value.strip()
            if name:
                self.dismiss(Task(name, category))
            else:
                self.dismiss(None)

        else:
            self.dismiss(None)


    def on_list_view_highlighted(self, event: ListView.Highlighted):
        category_input = self.query_one("#category", Input)
        label = event.item.query_one(Label)

        category_input.value = str(label.render())