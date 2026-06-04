import os
from metrics import faithfulness_metric, semantic_capture_metric
from test_helpers import load_test_cases, run_evaluation

METRICS = [faithfulness_metric, semantic_capture_metric]
EXPERIMENTS_DIR = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "experiments")

if __name__ == "__main__":
    run_evaluation(
        load_test_cases(EXPERIMENTS_DIR, "extraction.txt", "situation.json"),
        METRICS,
        "test-results/sonnet/extraction-tests.json"
    )
