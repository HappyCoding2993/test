from __future__ import annotations

import argparse
from pathlib import Path

from app.task_manager import TaskManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="简单任务管理 CLI")
    parser.add_argument(
        "--store",
        default=".data/tasks.json",
        help="任务存储路径（默认：.data/tasks.json）",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="新增任务")
    add_parser.add_argument("title", help="任务标题")

    done_parser = subparsers.add_parser("done", help="完成任务")
    done_parser.add_argument("--id", type=int, required=True, help="任务 ID")

    del_parser = subparsers.add_parser("delete", help="删除任务")
    del_parser.add_argument("--id", type=int, required=True, help="任务 ID")

    subparsers.add_parser("list", help="列出任务")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    manager = TaskManager(Path(args.store))

    if args.command == "add":
        task = manager.add_task(args.title)
        print(f"已新增任务 #{task.id}: {task.title}")
    elif args.command == "done":
        task = manager.complete_task(args.id)
        print(f"已完成任务 #{task.id}: {task.title}")
    elif args.command == "delete":
        manager.delete_task(args.id)
        print(f"已删除任务 #{args.id}")
    elif args.command == "list":
        tasks = manager.list_tasks()
        if not tasks:
            print("暂无任务")
            return
        for task in tasks:
            status = "✅" if task.done else "⬜"
            print(f"{status} #{task.id} {task.title}")


if __name__ == "__main__":
    main()
