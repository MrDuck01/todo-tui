"""
Docstring for ui.status_picker
"""

"""
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.styles import Style
"""
from prompt_toolkit.shortcuts.dialogs import radiolist_dialog

from core.status import ORDER, DISPLAY

async def pick_status_async(current_status):

    values = [
        (status, DISPLAY[status])
        for status in ORDER
    ]

    return await radiolist_dialog(
        title = "Change Status",
        text = "Select new status: ",
        values = values,
        ok_text=  "OK",
        cancel_text="Cancel",
        default = current_status,
    ).run_async()

"""
def pick_status(current_status):
    index = ORDER.index(current_status)

    def get_text():
        lines = []
        for i, status in enumerate(ORDER):
            prefix = "> " if i == index else " "
            lines.append(
                ("class:selected" if i == index else "class:text",
                 f"{prefix}{DISPLAY[status]}\n")
            )
        return lines

    kb = KeyBindings()

    @kb.add("up")
    def up(event):
        nonlocal index
        index = (index - 1) % len(ORDER)
    
    @kb.add("down")
    def down(event):
        nonlocal index
        index = (index + 1) % len(ORDER)
    
    @kb.add("enter")
    def accept(event):
        event.app.exit(result=ORDER[index])
    
    @kb.add("escape")
    def cancel(event):
        event.app.exit(result = None)

    app = Application(
        layout = Layout(
            Frame(
                Window(FormattedTextControl(get_text)),
                title = "Change Status"
            )
        ),
        key_bindings=kb,
        style=Style.from_dict({
            "selected": "reverse",
        }),
        full_screen=False
    )

    return app.run()
"""