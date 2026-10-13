"""SIG·BENCH — benchmark lokalnych LLM po polsku."""
from .runner import run_benchmark
from .tasks import default_tasks

__version__ = "1.0.0"
__all__ = ["run_benchmark", "default_tasks", "__version__"]
