from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, TypedDict


class Reminder(TypedDict):
    due_date: float


class State(TypedDict):
    remaining: List[int]
    reminders: Dict[int, Reminder]


class StateManager:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, all_ids: Iterable[int]) -> State:
        all_ids = list(dict.fromkeys(all_ids))  # preserve order and dedup
        valid_ids = set(all_ids)
        if not self.path.exists():
            state: State = {"remaining": list(all_ids), "reminders": {}}
            self.save(state)
            return state

        try:
            raw = json.loads(self.path.read_text())
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"State file {self.path} is not valid JSON. "
                "Fix or delete it before continuing."
            ) from e

        remaining: List[int] = []
        for problem_id in raw.get("remaining", []):
            if problem_id in valid_ids:
                remaining.append(problem_id)

        reminders: Dict[int, Reminder] = {}
        for problem_id, value in raw.get("reminders", {}).items():
            if problem_id not in valid_ids:
                continue
            if isinstance(value, dict) and "due_date" in value:
                reminders[problem_id] = {
                    "due_date": float(value["due_date"])
                }

        state: State = {"remaining": remaining, "reminders": reminders}
        self.save(state)
        return state

    def save(self, state: State) -> None:
        self.path.write_text(json.dumps(state, indent=2))

    def reset(self, all_ids: Iterable[int]) -> State:
        state: State = {"remaining": list(all_ids), "reminders": {}}
        self.save(state)
        return state

    def mark_completed(self, state: State, problem_id: int) -> State:
        remaining: List[int] = list(state.get("remaining", []))
        if problem_id not in remaining:
            return state
        remaining = [id for id in remaining if id != problem_id]
        reminders = state.get("reminders", {}).copy()
        reminders.pop(problem_id, None)
        updated: State = {"remaining": remaining, "reminders": reminders}
        self.save(updated)
        return updated

    def unmark_completed(
        self, state: State, all_ids: Iterable[int], problem_id: int
    ) -> State:
        all_ids = list(all_ids)
        if problem_id not in all_ids:
            return state

        remaining_set = set(state.get("remaining", []))
        if problem_id in remaining_set:
            return state

        remaining_set.add(problem_id)
        ordered = [id for id in all_ids if id in remaining_set]
        reminders = state.get("reminders", {}).copy()
        reminders.pop(problem_id, None)
        updated: State = {"remaining": ordered, "reminders": reminders}
        self.save(updated)
        return updated

    def schedule_reminder(
        self, state: State, problem_id: int, due_date: float
    ) -> State:
        reminders = state.get("reminders", {}).copy()
        reminders[problem_id] = {"due_date": due_date}
        updated: State = {"remaining": list(state["remaining"]), "reminders": reminders}
        self.save(updated)
        return updated
