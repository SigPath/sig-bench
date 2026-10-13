"""Modele danych SIG·BENCH."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskResult:
    task: str
    score: float  # 0.0 .. 1.0
    latency_s: float
    tok_s: float  # szybkość generowania (0, gdy provider nie mierzy)
    output: str


@dataclass
class ModelResult:
    model: str
    results: List[TaskResult] = field(default_factory=list)

    @property
    def mean_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    @property
    def mean_latency_s(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.latency_s for r in self.results) / len(self.results)

    @property
    def mean_tok_s(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.tok_s for r in self.results) / len(self.results)
