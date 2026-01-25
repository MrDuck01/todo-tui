from textual.screen import ModalScreen
from textual.widgets import Input, Button
from textual.containers import Vertical

from core.task import Task

class AddTaskScreen(ModalScreen[Task | None]):
    def compose(self):
        yield Vertical(
            Input(placeholder = "Task name", id="name"),
            Button("Add", id="add"),
            Button("Cancel", id="cancel"),
        )


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add":
            name = self.query_one("#name", Input).value.strip()
            if name:
                self.dismiss(Task(name))
            else:
                self.dismiss(None)

        else:
            self.dismiss(None)