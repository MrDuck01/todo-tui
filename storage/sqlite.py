import sqlite3
from datetime import datetime
from core.task import Task
from core.status import Status

DB_FILE = "tasks.db"

def get_connection():
    return sqlite3.Connection(DB_FILE)

def init_db():
    with get_connection() as conn:
        conn.execute("""
        create table if not exists tasks(
            id text primary key,
            name text not null,
            status text not null,
            created_at text not null,
            last_updated text not null,
            completed_at text
        )
        """)

def insert_task(task):
    with get_connection() as conn:
        conn.execute("""
        insert into tasks values(?, ?, ?, ?, ?, ?)
        """, (
            task.id,
            task.name,
            task.status.value,
            task.create_at.isoformat(),
            task.last_updated.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None
        ))

def get_all_tasks():
    tasks = []

    with get_connection() as conn:
        rows = conn.execute("select * from tasks").fetchall()

    for row in rows:
        task = Task(row[1])
        task.id = row[0]
        task.status = Status(row[2])
        task.create_at = datetime.fromisoformat(row[3])
        task.last_updated = datetime.fromisoformat(row[4])
        task.completed_at = (
                datetime.fromisoformat(row[5]) if row[5] else None
        )
        tasks.append(task)

    return tasks

def update_task_status(task, status, last_updated, completed_at):
    with get_connection() as conn:
        conn.execute("""
                     update tasks
                     set
                        status = ?,
                        last_updated = ?,
                        completed_at = ?
                     where id = ?
                     """, (
                         status.value,
                         last_updated.isoformat(),
                         completed_at.isoformat() if completed_at else None,
                         task.id
                     ))


def delete_task(task):
    with get_connection() as conn:
        conn.execute("""
                    delete from tasks
                    where id = ?
                    """, (task.id,)
        )