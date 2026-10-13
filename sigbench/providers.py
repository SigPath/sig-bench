"""Providerzy modeli: Ollama (rzeczywisty) i Echo (deterministyczny, do testów/demo)."""
import json
import time
import urllib.error
import urllib.request
from typing import Dict, List


class Provider:
    """Kontrakt: zwraca (tekst, tok_s) dla promptu; tok_s=0.0, gdy nie mierzone."""

    def generate(self, model: str, prompt: str) -> Dict:
        raise NotImplementedError


class OllamaProvider(Provider):
    """Lokalny Ollama (http://localhost:11434). Bez zależności — stdlib."""

    def __init__(self, host: str = "http://localhost:11434", timeout_s: int = 120):
        self.host = host.rstrip("/")
        self.timeout_s = timeout_s

    def generate(self, model: str, prompt: str) -> Dict:
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            data = json.loads(resp.read().decode())
        latency = time.perf_counter() - t0

        text = data.get("response", "")
        eval_count = int(data.get("eval_count") or 0)
        eval_duration = float(data.get("eval_duration") or 0)  # nanosekundy
        tok_s = eval_count / (eval_duration / 1e9) if eval_duration > 0 and eval_count else 0.0
        return {"text": text, "latency_s": latency, "tok_s": tok_s}

    def list_models(self) -> List[str]:
        with urllib.request.urlopen(f"{self.host}/api/tags", timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return [m["name"] for m in data.get("models", [])]


class EchoProvider(Provider):
    """Deterministyczny provider do testów i demo raportu.

    ``good=False`` odpowiada poprawnie tylko na część zadań (wynik ~0.4),
    ``good=True`` na wszystkie — dzięki temu demo raportu pokazuje rozrzut.
    """

    def __init__(self, good: bool = False):
        self.good = good

    def generate(self, model: str, prompt: str) -> Dict:
        t0 = time.perf_counter()
        if "Ania" in prompt:
            text = "Ania ma 4 jabłka."
        elif "Przetłumacz" in prompt:
            text = "Pogoda jest dziś piękna." if self.good else "The weather is beautiful today."
        elif "Australii" in prompt:
            text = "Canberra" if self.good else "Sydney"
        elif "20 słowach" in prompt:
            if self.good:
                text = "Maszyny pracują bez przerwy, koszty spadają, a pracownicy muszą się przekwalifikować."
            else:
                text = prompt.split(":", 1)[1].strip()  # „streszczenie” = wklejenie całości
        elif "numerowaną" in prompt:
            text = "1. czerwony\n2. zielony\n3. niebieski"
        else:
            text = "(echo)"
        latency = max(time.perf_counter() - t0, 0.001)
        return {"text": text, "latency_s": latency, "tok_s": 0.0}


class HttpError(RuntimeError):
    def __init__(self, model: str, cause: urllib.error.URLError):
        super().__init__(
            f"Nie mogę dosięgnąć modelu '{model}': {cause}. "
            "Czy Ollama działa? (ollama serve, a potem: ollama pull <model>)"
        )
