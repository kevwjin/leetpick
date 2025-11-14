#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
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

    subparsers.add_parser(
        "pick", help="Pick a random incomplete problem")
    subparsers.add_parser(
        "status", help="Show progress")
    toggle_parser = subparsers.add_parser(
        "toggle", help="Toggle completion for a problem")
    toggle_parser.add_argument(
        "problem_id", type=int, help="LeetCode problem number to toggle completion for")
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
    problem_id = random.choice(remaining)
    record = dataset.index[problem_id]

    # do not show topic when suggesting
    print(
        f'Suggested: [{record["difficulty"]}] '
        f'{record["title"]}'  # — {record["topic"]}'
    )
    print(record["link"])
    print(f'Use "toggle {problem_id}" to mark complete when done.')


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
        case "reset":
            cmd_reset(args)
        case _:
            parser.error("Unknown command")


if __name__ == "__main__":
    main()
