from datetime import datetime
import uuid

from core.status import Status, ORDER

class Task: 

    def __init__(self, name, _id=None):
        self.id = _id or str(uuid.uuid4())
        self.name = name
        self.status = Status.ACTIVE
        
        now = datetime.now()
        self.create_at = now
        self.last_updated = now
        self.completed_at = None
        
    def mark_complete(self):
        self.status = "complete"
        self.completed_at = datetime.now()
        self.last_updated = self.completed_at
        
    def __str__(self):
        return f"[{self.status}] {self.name}"
    
    def to_line(self):
        return "|".join([
            self.id,
            self.name,
            self.status,
            self.create_at.isoformat(),
            self.last_updated.isoformat(),
            self.completed_at.isoformat() if self.completed_at else ""
        ])
    
    def cycle_status(self):
        i = ORDER.index(self.status)
        next_status = ORDER[i+1 % len(ORDER)]

        self.set_status(next_status)
    
    @staticmethod
    def from_line(line):
        parts = line.strip().split("|")
        
        if len(parts) != 6:
            raise ValueError(f"Incomplete number of parts being stored {line}")
        
        task = Task(parts[1], _id=parts[0])
        task.status = parts[2]
        task.created_at = datetime.fromisoformat(parts[3])
        task.last_updated = datetime.fromisoformat(parts[4])
        task.completed_at = (
            datetime.fromisoformat(parts[5]) if parts[5] else None
        )
        
        return task
    
    def set_status(self, status: Status):
        self.status = status
        self.last_updated = datetime.now()

        if status == Status.COMPLETED:
            self.completed_at = self.last_updated
        else:
            self.completed_at = None

    def __str__(self):
        return f"[{self.status.value}] {self.name}"
    
