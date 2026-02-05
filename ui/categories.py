
from textual.screen import ModalScreen
from textual.widgets import Button, Input, ListItem, ListView, Label
from textual.containers import Vertical

from storage import sqlite as storage

class CategoryPicker(ModalScreen[str | None]):
    def compose(self):
        categorys = storage.get_categorys()
        yield ListView(
            *[ListItem(category) for category in categorys],
            id="categorys"
        )

    def on_list_view_selected(self, event: ListView.Selected):
        self.dismiss(event.item.query_one(Label).render())