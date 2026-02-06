
from ast import Yield
from textual.screen import ModalScreen
from textual.widgets import Button, Input, ListItem, ListView, Label
from textual.containers import Vertical

from storage import sqlite as storage

class CategoryPicker(ModalScreen[str | None]):
    def compose(self):
        categorys = storage.get_categorys()
        yield Vertical(
             ListView(
                *[ListItem(Label(category)) for category in categorys],
                id="categorys"
            ),
            Button("Select", id="select"),
            Button("Cancel", id="cancel"),
        )

    def on_list_view_selected(self, event: ListView.Selected):
        self.dismiss(event.item.query_one(Label).render())
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "select":
            list_view = self.query_one("#categorys", ListView)
            selected = list_view.index
            if selected is not None:
                category = list_view.children[selected].query_one(Label).render()
                self.dismiss(category)
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)
            