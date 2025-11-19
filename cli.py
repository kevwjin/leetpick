#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from leetpick.data_loader import load_dataset
from leetpick.state_manager import StateManager

DEFAULT_DATASET = Path("datasets/nc250_geMed.json")
DEFAULT_STATE = Path(".state") / "nc250_geMed_state.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Randomly pick LeetCode problems from a problem bank "
            "without repeating completed problems."
        ),
        epilog=(
            "The problem bank is initialized with the full list of "
            "problems loaded from the dataset. Problems marked complete are "
            "removed from the problem bank until they are unmarked or "
            "until you run `reset`."
        )
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET),
        help="Path to dataset JSON (default: datasets/nc250_geMed.json)",
    )
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE),
        help=(
            "Path to state file "
            "(default: ./.state/nc250_geMed_state.json)"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    pick_parser = subparsers.add_parser(
        "pick", help="Pick random incomplete problems")
    pick_parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of suggestions to display (default: 1)",
    )
    subparsers.add_parser(
        "status", help="Show progress")

    toggle_parser = subparsers.add_parser(
        "toggle", help="Toggle completion for a problem")
    toggle_parser.add_argument(
        "problem_id", type=int, help="LeetCode problem number to toggle completion for")

    remind_parser = subparsers.add_parser(
        "remind", help="Schedule a reminder to revisit a problem")
    remind_parser.add_argument(
        "problem_id",
        type=int,
        help="LeetCode problem number to schedule",
    )
    remind_parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Days until the reminder is due (default: 3)",
    )
    list_parser = subparsers.add_parser(
        "list", help="List completed problems or reminders"
    )
    list_parser.add_argument(
        "category",
        choices=["completed", "reminders"],
        help="Which list to show",
    )

    subparsers.add_parser(
        "reset",
        help="Reset all progress",
        description=(
            "Unmark completion for all problems so they can be picked again."
        )
    )
    return parser


def load_context(args: argparse.Namespace):
    dataset = load_dataset(Path(args.dataset).expanduser())
    manager = StateManager(Path(args.state).expanduser())
    return dataset, manager


def cmd_pick(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    state = manager.load(dataset.ids)
    remaining = state["remaining"]
    if not remaining:
        print(
            "All problems marked completed. "
            "To continue, reset or toggle problem completion(s)."
        )
        return

    today = datetime.now().date()
    reminders = state.get("reminders", {})
    due_ids = []
    for id_, reminder in reminders.items():
        reminder_day = datetime.fromtimestamp(reminder["due_date"]).date()
        if reminder_day <= today:
            due_ids.append(id_)
    due_ids.sort(key=lambda id_: reminders[id_]["due_date"])
    if due_ids:
        print("Reminder(s):")
        for id_ in due_ids:
            record = dataset.index.get(id_)
            if not record:
                continue
            print(f" - {id_} [{record['difficulty']}] {record['link']}")

    count = max(1, getattr(args, "count", 1))
    if count > len(remaining):
        count = len(remaining)

    suggestions = random.sample(remaining, count)
    print("Suggestion(s):")
    for suggestion_id in suggestions:
        record = dataset.index[suggestion_id]
        print(
            f" - [{record['difficulty']}] {record['link']}"
        )
        print(
            f"   Use `leetpick toggle {suggestion_id}` "
            "to mark complete when done."
        )


def cmd_status(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    state = manager.load(dataset.ids)
    remaining = state.get("remaining", [])

    total = len(dataset.records)
    completed = total - len(remaining)
    print(f"{completed}/{total} completed ({completed / total:.1%})")


def cmd_reset(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    manager.reset(dataset.ids)
    print("Progress reset. Problem bank refilled with all problems.")


def cmd_toggle(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    state = manager.load(dataset.ids)
    problem_id = args.problem_id

    if problem_id not in dataset.index:
        print(f"Problem id {problem_id} not found in this problem bank.")
        return

    if problem_id in state["remaining"]:
        manager.mark_completed(state, problem_id)
        print(f"Marked {problem_id} as complete.")
    else:
        manager.unmark_completed(state, dataset.ids, problem_id)
        print(f"Moved {problem_id} back into the problem bank.")


def cmd_remind(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    state = manager.load(dataset.ids)
    problem_id = args.problem_id

    if problem_id not in dataset.index:
        print(f"Problem id {problem_id} not found in this problem bank.")
        return

    days = max(0, args.days)
    due_at = time.time() + timedelta(days=days).total_seconds()
    manager.schedule_reminder(state, problem_id, due_at)
    due_str = datetime.fromtimestamp(due_at).strftime("%Y-%m-%d")
    print(
        f"Reminder set for problem {problem_id} on {due_str} "
        f"(in {days} day(s))."
    )


def cmd_list(args: argparse.Namespace) -> None:
    dataset, manager = load_context(args)
    state = manager.load(dataset.ids)
    category = args.category

    if category == "completed":
        remaining = set(state.get("remaining", []))
        completed_ids = [id_ for id_ in dataset.ids if id_ not in remaining]
        if not completed_ids:
            print(f"{len(completed_ids)} completed problem(s)")
            return
        print(f"{len(completed_ids)} completed problem(s):")
        for id_ in completed_ids:
            record = dataset.index[id_]
            print(f" - {id_}. [{record['difficulty']}] {record['link']}")
    elif category == "reminders":
        reminders = state.get("reminders", {})
        items = sorted(reminders.items(), key=lambda kv: kv[1]["due_date"])
        if not items:
            print(f"{len(items)} reminder(s)")
            return
        print(f"{len(items)} reminder(s):")
        for id_, info in items:
            record = dataset.index.get(id_)
            if not record:
                continue
            due_str = datetime.fromtimestamp(info["due_date"]).strftime(
                "%Y-%m-%d"
            )
            print(
                f" - {id_}. [{record['difficulty']}] {record['link']} "
                f"(due {due_str})"
            )


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    match args.command:
        case "pick":
            cmd_pick(args)
        case "status":
            cmd_status(args)
        case "toggle":
            cmd_toggle(args)
        case "remind":
            cmd_remind(args)
        case "list":
            cmd_list(args)
        case "reset":
            cmd_reset(args)
        case _:
            parser.error("Unknown command")


if __name__ == "__main__":
    main()
