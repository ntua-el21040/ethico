from pathlib import Path
from test_helpers import load_conversational_test_cases, run_evaluation
from metrics import relevance_metric, knowledge_retention_metric
 
PATTERN = str(Path(__file__).parent.parent / "experiments" / "*" / "extraction.txt")
print(f"Loading test cases from pattern: {PATTERN}")
METRICS = [relevance_metric, knowledge_retention_metric]
 
if __name__ == "__main__":
    dataset = load_conversational_test_cases(PATTERN)
    run_evaluation(dataset, METRICS, "test-results/sonnet/conversational-tests.json")