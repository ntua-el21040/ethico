import json
import os
from src.validator import KantianModel

situation_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "situation.json",
)

def test_dilemma_correctness():
    """
    Validates the output of the evaluate_dilemma function.
    """
    from src.evaluator import evaluate_dilemma

    evaluate_dilemma()

    with open(situation_path, "r") as f:
        model_data = json.load(f)
    
    KantianModel.model_validate(model_data)