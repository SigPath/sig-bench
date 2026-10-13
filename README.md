# SIG·BENCH

**Benchmark lokalnych LLM po polsku** — jakość odpowiedzi, latencja i tok/s na Twoim
sprzęcie. Jedno polecenie → jeden samodzielny raport HTML, który możesz komuś wysłać.

→ **Przykładowy raport:** https://sigpath.github.io/sig-bench/ (tryb demo na providerze Echo)

## Co robi

1. Pyta każdy model o **5 zadań po polsku**: logika, tłumaczenie EN→PL, wiedza,
   streszczenie z limitem słów, przestrzeganie formatu — każde z jednoznacznym checkerem,
2. mierzy **latencję** i **tok/s** (z liczników Ollama),
3. zapisuje **jeden plik `report.html`** (inline CSS, bez zależności) z tabelą i szczegółami,
4. awaria jednego zadania nie przerywa benchmarku — trafia do raportu jako BŁĄD.

## Szybki start

```bash
# wymagany działający Ollama + wypullowane modele
ollama pull llama3.2

# opcja A: z repo (uv)
uv run sigbench run --models llama3.2,qwen2.5:7b --runs 3

# opcja B: z repo (pip)
pip install . && sigbench run --models llama3.2 --runs 3

# demo bez Ollamy (deterministyczny provider Echo):
python3 -m sigbench run --demo --out docs/index.html
```

Wynik: `out/report.html` — otwórz dwuklikiem lub wrzuć gdziekolwiek.

## Interpretacja

| Kolumna | Znaczenie |
|---|---|
| Wynik | % zaliczonych zadań (0–100%) — jakość po polsku |
| Latencja | średni czas pełnego zapytania |
| Tok/s | szybkość generowania (z `eval_count`/`eval_duration` Ollamy) |

Zestaw 5 zadań jest celowo mały i szybki: to dymny test porównawczy na własnym
sprzęcie, nie akademicki benchmark. Zadania dodasz w `sigbench/tasks.py` —
każde to prompt + funkcja sprawdzająca 0..1.

## Testy

```bash
python3 tests/test_sigbench.py   # 9 testów, same biblioteki standardowe
```

CI na GitHub Actions uruchamia testy i generuje raport demo.

## Licencja

MIT
