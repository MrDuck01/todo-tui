from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label
from core.status import Status


class StatusItem(ListItem):
    def __init__(self, status: Status):
        self.status = status
        super().__init__(Label(status.value))

class StatusPicker(ModalScreen):
    def compose(self):
        yield ListView(
            *[StatusItem(s) for s in Status]
            # *[ListItem(Label(s.value)) for s in Status]
        )
    
    def on_list_view_selected(self, event: ListView.Selected):
        # staus = Status(event.item.query_one(Label).text)
        # self.dismiss(event.item.status)
        self.dismiss(Status(event.item.query_one(Label).render()))
