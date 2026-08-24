"""Phase 5 evaluation layer. Does not modify AdaptiveTutor."""

from adapt.eval.baseline import LinearTutor
from adapt.eval.constants import BENCHMARK_VERSION, RANDOM_SEED
from adapt.eval.experiment import run_adapt_training, run_baseline_training
from adapt.eval.materials import POSTTEST_ADAPT, POSTTEST_BASELINE, PRETEST
from adapt.eval.scoring import learning_gain, score_test

__all__ = [
    "BENCHMARK_VERSION",
    "LinearTutor",
    "POSTTEST_ADAPT",
    "POSTTEST_BASELINE",
    "PRETEST",
    "RANDOM_SEED",
    "learning_gain",
    "run_adapt_training",
    "run_baseline_training",
    "score_test",
]
