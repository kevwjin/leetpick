from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Dataset:
    records: List[dict]
    index: Dict[int, dict]

    @property
    def ids(self) -> List[int]:
        return list(self.index.keys())


def load_dataset(path: Path) -> Dataset:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"dataset not found at {path}")

    records = json.loads(path.read_text())
    index = {record['id']: record for record in records}
    return Dataset(records=records, index=index)
