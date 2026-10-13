"""Testy SIG·BENCH — uruchamiane systemowym python3 (3.9+), bez zależności."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sigbench.models import ModelResult, TaskResult  # noqa: E402
from sigbench.providers import EchoProvider  # noqa: E402
from sigbench.report import render_report  # noqa: E402
from sigbench.runner import run_benchmark  # noqa: E402
from sigbench.tasks import default_tasks  # noqa: E402


class TestTasks(unittest.TestCase):
    def test_checkers_maja_zakres_0_1(self):
        for task in default_tasks():
            for sample in ["", "x", "1. czerwony\n2. zielony\n3. niebieski", "Canberra", "4"]:
                score = task.check(sample)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_logika_poprawna_odpowiedz(self):
        logika = {t.name: t for t in default_tasks()}["logika"]
        self.assertEqual(logika.check("Ania ma 4 jabłka."), 1.0)
        self.assertEqual(logika.check("Ania ma 5 jabłek."), 0.0)


class TestEchoProvider(unittest.TestCase):
    def setUp(self):
        self.provider = EchoProvider(good=False)
        self.tasks = default_tasks()

    def test_deterministyczny(self):
        a = self.provider.generate("m", self.tasks[0].prompt)
        b = self.provider.generate("m", self.tasks[0].prompt)
        self.assertEqual(a["text"], b["text"])

    def test_slaby_model_ma_rozrzut_wynikow(self):
        results = run_benchmark(["echo"], self.tasks, EchoProvider(good=False), runs=1)
        scores = [r.score for r in results[0].results]
        self.assertLess(min(scores), max(scores))  # częściowo dobrze, częściowo źle
        self.assertAlmostEqual(results[0].mean_score, 0.4, places=6)  # 2/5 zadań

    def test_dobry_model_zdobywa_wszystko(self):
        results = run_benchmark(["echo+"], self.tasks, EchoProvider(good=True), runs=1)
        self.assertAlmostEqual(results[0].mean_score, 1.0, places=6)


class TestRunner(unittest.TestCase):
    def test_runs_zero_rzuca(self):
        with self.assertRaises(ValueError):
            run_benchmark(["m"], default_tasks(), EchoProvider(), runs=0)

    def test_struktura_wynikow(self):
        results = run_benchmark(["a", "b"], default_tasks(), EchoProvider(good=True), runs=2)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(len(r.results), len(default_tasks()) * 2)
        self.assertEqual(results[0].mean_score, results[1].mean_score)


class TestAggregation(unittest.TestCase):
    def test_srednie(self):
        r = ModelResult(model="x", results=[
            TaskResult("a", 1.0, 1.0, 10.0, ""),
            TaskResult("b", 0.0, 3.0, 20.0, ""),
        ])
        self.assertAlmostEqual(r.mean_score, 0.5)
        self.assertAlmostEqual(r.mean_latency_s, 2.0)
        self.assertAlmostEqual(r.mean_tok_s, 15.0)


class TestReport(unittest.TestCase):
    def test_raport_zawiera_modele_i_styl(self):
        results = run_benchmark(["echo-basic", "echo-plus"], default_tasks(), EchoProvider(good=True), runs=1)
        html = render_report(results)
        self.assertIn("echo-basic", html)
        self.assertIn("echo-plus", html)
        self.assertIn("SIG·BENCH", html)
        self.assertIn("score-bar", html)
        self.assertNotIn("{_CSS}", html)


if __name__ == "__main__":
    unittest.main()
