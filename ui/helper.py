from collections import Counter
from core.status import Status

def get_task_counts(tasks):
    counts = Counter(task.status for task in tasks)

    return {
        "total": len(tasks),
        Status.ACTIVE: counts.get(Status.ACTIVE, 0),
        Status.IN_PROGRESS: counts.get(Status.IN_PROGRESS, 0),
        Status.HOLD: counts.get(Status.HOLD, 0),
        Status.CANCELLED: counts.get(Status.CANCELLED,0),
    }

def get_footer_text():
    return[
        ("class:footer", " ↑↓ "),
        ("class:key", "Navigate"),
        ("class:footer", "  Enter "),
        ("class:key", "Toggle"),
        ("class:footer", "  A "),
        ("class:key", "Add"),
        ("class:footer", "  S "),
        ("class:key", "Status"),
        ("class:footer", "  D "),
        ("class:key", "Delete"),
        ("class:footer", "  Q "),
        ("class:key", "Quit"),
    ]