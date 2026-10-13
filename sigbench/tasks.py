"""Zadania benchmarku po polsku — każde z jednoznacznym checkerem."""
from dataclasses import dataclass
from typing import Callable


@dataclass
class Task:
    name: str
    prompt: str
    check: Callable[[str], float]
    description: str


def _contains_any(text: str, needles) -> float:
    low = text.lower()
    return 1.0 if any(n.lower() in low for n in needles) else 0.0


def _make_summary_check(max_words: int) -> Callable[[str], float]:
    def check(text: str) -> float:
        words = len(text.split())
        if words == 0:
            return 0.0
        # punkt za zwięzłość: dobrze, gdy wyraźnie krótsze niż limit
        return 1.0 if words <= max_words else 0.0
    return check


def default_tasks() -> list:
    return [
        Task(
            name="logika",
            description="Proste rozumowanie wieloetapowe",
            prompt=(
                "Odpowiedz krótko, samą odpowiedzią. Ania ma 3 jabłka, kupuje "
                "jeszcze 2, a potem daje 1 kursce. Ile jabłek ma Ania?"
            ),
            check=lambda t: _contains_any(t, ["4", "cztery"]),
        ),
        Task(
            name="tlumaczenie",
            description="Tłumaczenie EN→PL",
            prompt="Przetłumacz na polski (tylko tłumaczenie): 'The weather is beautiful today.'",
            check=lambda t: _contains_any(t, ["pogoda", "piękna", "piekna"]),
        ),
        Task(
            name="wiedza",
            description="Faktografia",
            prompt="Jaka jest stolica Australii? Odpowiedz jednym słowem.",
            check=lambda t: _contains_any(t, ["canberra"]),
        ),
        Task(
            name="streszczenie",
            description="Streszczenie w maks. 20 słowach",
            prompt=(
                "Streść w maksymalnie 20 słowach: Roboty przemysłowe zmieniają "
                "produkcję. Linie montażowe pracują dniem i nocą bez przerwy, a czujniki "
                "muszą się przekwalifikować, by obsługiwać nowe maszyny."
            ),
            check=_make_summary_check(20),
        ),
        Task(
            name="formatowanie",
            description="Przestrzeganie formatu (lista)",
            prompt="Wypisz 3 kolory jako listę numerowaną (1., 2., 3.). Tylko lista.",
            check=lambda t: 1.0 if ("1." in t and "2." in t and "3." in t) else 0.0,
        ),
    ]
