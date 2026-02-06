
from ast import Yield
from textual.screen import ModalScreen
from textual.widgets import Button, Input, ListItem, ListView, Label, RadioButton, RadioSet
from textual.containers import Vertical

from storage import sqlite as storage

class CategoryPicker(ModalScreen[tuple[str, bool] | None]):
    def compose(self):
        categorys = storage.get_categorys()
        yield Vertical(
             ListView(
                *[ListItem(Label(category)) for category in categorys],
                id="categorys"
            ),
            RadioSet(
                RadioButton("Include", id="include"),
                RadioButton("Exclude", id="exclude"),
                id = "mode"
            ),
            Button("Select", id="select"),
            Button("Cancel", id="cancel"),
        )

    def _get_selected_category(self) -> str | None:
        list_view = self.query_one("#categories", ListView)
        if list_view.index is None:
            return None
        
        label = list_view.children[list_view.index].query_one(Label)
        return str(label.renderable)

    def _get_mode(self) -> bool:
        radios = self.query_one("#mode#", RadioSet)
        return radios.pressed == "include"
    
    def on_list_view_selected(self, event: ListView.Selected):
        self.dismiss(event.item.query_one(Label).render())
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "select":
            category = self._get_selected_category()
            if category is None:
                self.dismiss(None)
                return
            
            include = self._get_mode()
            self.dismiss((category, include))            
        else:
                self.dismiss(None)