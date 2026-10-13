"""CLI SIG·BENCH:  python -m sigbench run --models llama3.2 --runs 3"""
import argparse
import sys
from typing import List

from .providers import EchoProvider, OllamaProvider
from .report import render_report
from .runner import run_benchmark
from .tasks import default_tasks


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sigbench",
        description="Benchmark lokalnych LLM (Ollama): jakość na zadaniach PL + tok/s + latencja.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="uruchom benchmark i zapisz raport")
    run_p.add_argument("--models", default="", help="modele po przecinku (np. llama3.2,qwen2.5). Puste = wszystkie z Ollamy")
    run_p.add_argument("--runs", type=int, default=3, help="powtórzenia każdego zadania (domyślnie 3)")
    run_p.add_argument("--host", default="http://localhost:11434", help="adres Ollama")
    run_p.add_argument("--out", default="out/report.html", help="ścieżka raportu HTML")
    run_p.add_argument("--demo", action="store_true", help="tryb demo na providerze Echo (bez Ollamy)")

    args = parser.parse_args(argv)
    if args.cmd != "run":  # pragma: no cover
        parser.error("nieznana komenda")

    tasks = default_tasks()
    if args.demo:
        runs = max(1, args.runs)
        results = run_benchmark(["echo-basic"], tasks, EchoProvider(good=False), runs=runs) \
            + run_benchmark(["echo-plus"], tasks, EchoProvider(good=True), runs=runs)
    else:
        provider = OllamaProvider(host=args.host)
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        if not models:
            try:
                models = provider.list_models()
            except Exception as e:
                print(f"BŁĄD: {e}", file=sys.stderr)
                return 2
        if not models:
            print("BŁĄD: brak modeli. Ściągnij np.: ollama pull llama3.2", file=sys.stderr)
            return 2
        print(f"Benchmark {len(models)} modeli × {len(tasks)} zadań × {args.runs} powtórzeń…")
        results = run_benchmark(
            models=models,
            tasks=tasks,
            provider=provider,
            runs=args.runs,
            on_progress=lambda m, t, s: print(f"  {m} · {t} → {s * 100:.0f}%"),
        )

    html = render_report(results)
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Raport: {args.out}")

    results.sort(key=lambda r: r.mean_score, reverse=True)
    print("\n== Podsumowanie ==")
    for r in results:
        print(f"  {r.model:24s} wynik {r.mean_score * 100:5.0f}%  latencja {r.mean_latency_s:5.2f}s  tok/s {r.mean_tok_s:6.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
