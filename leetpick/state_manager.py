from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, TypedDict


class State(TypedDict):
    remaining: List[int]


class StateManager:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, all_ids: Iterable[int]) -> State:
        all_ids = list(dict.fromkeys(all_ids))  # preserve order and dedup
        valid_ids = set(all_ids)
        if not self.path.exists():
            state: State = {"remaining": list(all_ids)}
            self.save(state)
            return state

        try:
            raw = json.loads(self.path.read_text())
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"State file {self.path} is not valid JSON. "
                "Fix or delete it before continuing."
            ) from e

        remaining = \
            [id for id in raw.get("remaining", []) if id in valid_ids]

        state: State = {"remaining": remaining}
        self.save(state)
        return state

    def save(self, state: State) -> None:
        self.path.write_text(json.dumps(state, indent=2))

    def reset(self, all_ids: Iterable[int]) -> State:
        state: State = {"remaining": list(all_ids)}
        self.save(state)
        return state

    def mark_completed(self, state: State, problem_id: int) -> State:
        remaining: List[int] = list(state.get("remaining", []))
        if problem_id not in remaining:
            return state
        remaining = [id for id in remaining if id != problem_id]
        updated: State = {"remaining": remaining}
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
        updated: State = {"remaining": ordered}
        self.save(updated)
        return updated
