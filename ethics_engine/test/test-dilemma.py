import json
import os
from ethics.cam.principles import KantianHumanityPrinciple
from ethics.cam.semantics import CausalModel
from src.validator import KantianModel

situation_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cases",
    "trolley-problem.json",
)

def evaluate(situation_path):
    with open(situation_path, 'r') as f:
        model = json.load(f)

    KantianModel.model_validate(model)
    
    action = [a for a in model["actions"] if a != "refrain"][0]
    action_world = {action: 1, "refrain": 0}
    inaction_world = {action: 0, "refrain": 1}

    action_situation = CausalModel(situation_path, action_world)
    inaction_situation = CausalModel(situation_path, inaction_world)
    action_situation.alternatives.append(inaction_situation)
    inaction_situation.alternatives.append(action_situation)
    
    explanation = action_situation.explain(KantianHumanityPrinciple)
    
    print(explanation)
    return explanation

if __name__ == "__main__":
    evaluate(situation_path)