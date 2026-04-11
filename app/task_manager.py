from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import List


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


class TaskManager:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self._tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            self._tasks = []
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self._tasks = [Task(**item) for item in data]

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(task) for task in self._tasks]
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_tasks(self) -> List[Task]:
        return list(self._tasks)

    def add_task(self, title: str) -> Task:
        next_id = (max((task.id for task in self._tasks), default=0) + 1)
        task = Task(id=next_id, title=title)
        self._tasks.append(task)
        self._save()
        return task

    def complete_task(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                task.done = True
                self._save()
                return task
        raise ValueError(f"Task {task_id} 不存在")

    def delete_task(self, task_id: int) -> None:
        before = len(self._tasks)
        self._tasks = [task for task in self._tasks if task.id != task_id]
        if len(self._tasks) == before:
            raise ValueError(f"Task {task_id} 不存在")
        self._save()
