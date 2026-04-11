from pathlib import Path

from app.task_manager import TaskManager


def test_add_and_list_tasks(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    manager = TaskManager(store)

    manager.add_task("first")
    manager.add_task("second")

    tasks = manager.list_tasks()
    assert [t.id for t in tasks] == [1, 2]
    assert [t.title for t in tasks] == ["first", "second"]
    assert [t.done for t in tasks] == [False, False]


def test_complete_task_persists(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    manager = TaskManager(store)
    manager.add_task("persist me")

    manager.complete_task(1)

    reloaded = TaskManager(store)
    tasks = reloaded.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].done is True


def test_delete_task(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    manager = TaskManager(store)
    manager.add_task("to be deleted")

    manager.delete_task(1)

    assert manager.list_tasks() == []
