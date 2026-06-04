import os
from metrics import explanation_structure_metric, explanatory_value_metric
from test_helpers import load_test_cases, run_evaluation

METRICS = [explanation_structure_metric, explanatory_value_metric]
EXPERIMENTS_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "experiments")

if __name__ == "__main__":
    run_evaluation(
        load_test_cases(EXPERIMENTS_DIR, "evaluation.json", "explanation.txt"),
        METRICS,
        "test-results/sonnet/explanation-tests.json"
    )
