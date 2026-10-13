"""Runner: model × zadanie × powtórzenia → zagregowane wyniki."""
import time
from typing import Dict, List

from .models import ModelResult, TaskResult
from .providers import Provider
from .tasks import Task


def run_benchmark(
    models: List[str],
    tasks: List[Task],
    provider: Provider,
    runs: int = 1,
    on_progress=None,
) -> List[ModelResult]:
    if runs < 1:
        raise ValueError("runs musi być >= 1")
    results: Dict[str, ModelResult] = {m: ModelResult(model=m) for m in models}

    for model in models:
        for task in tasks:
            for _ in range(runs):
                t0 = time.perf_counter()
                try:
                    out = provider.generate(model, task.prompt)
                except Exception as e:  # awaria jednego zadania nie przerywa benchmarku
                    results[model].results.append(
                        TaskResult(task=task.name, score=0.0, latency_s=0.0, tok_s=0.0, output=f"BŁĄD: {e}")
                    )
                    if on_progress:
                        on_progress(model, task.name, 0.0)
                    continue
                latency = time.perf_counter() - t0
                score = task.check(out.get("text", ""))
                results[model].results.append(
                    TaskResult(
                        task=task.name,
                        score=score,
                        latency_s=out.get("latency_s", latency),
                        tok_s=out.get("tok_s", 0.0),
                        output=out.get("text", ""),
                    )
                )
                if on_progress:
                    on_progress(model, task.name, score)

    return list(results.values())
