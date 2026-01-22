from enum import Enum

class Status(Enum):
        ACTIVE= "active"
        IN_PROGRESS= "in_progress"
        HOLD= "hold"
        CANCELLED= "cancelled"
        COMPLETED= "completed"

ORDER = [
    Status.ACTIVE,
    Status.IN_PROGRESS,
    Status.HOLD,
    Status.CANCELLED,
    Status.COMPLETED
]

STYLES = {
    Status.ACTIVE: "class:text",
    Status.IN_PROGRESS: "class:progress",
    Status.HOLD: "class:hold",
    Status.CANCELLED: "class:cancelled",
    Status.COMPLETED: "class:completed"
}

DISPLAY={
    Status.ACTIVE: "Active",
    Status.IN_PROGRESS: "In Progress",
    Status.HOLD: "On Hold",
    Status.CANCELLED: "Cancelled",
    Status.COMPLETED: "Completed"
}   