import os
import json
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import KantianHumanityPrinciple, UtilitarianPrinciple


def evaluate_dilemma():
    """
    Reads a dilemma from data/situation.json and evaluates it using the Kantian Humanity Principle.
    The dilemma is always assumed to be valid.
    """
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    situation_path = os.path.join(data_dir, "situation.json")
    output_path = os.path.join(data_dir, "evaluation.json")

    with open(situation_path, "r") as f:
        model = json.load(f)

    action = [a for a in model["actions"] if a != "refrain"][0]
    action_world = {action: 1, "refrain": 0}
    inaction_world = {action: 0, "refrain": 1}

    action_situation = CausalModel(situation_path, action_world)
    inaction_situation = CausalModel(situation_path, inaction_world)
    action_situation.alternatives.append(inaction_situation)
    inaction_situation.alternatives.append(action_situation)

    result1 = action_situation.explain(KantianHumanityPrinciple)
    result2 = action_situation.explain(UtilitarianPrinciple)
    result = {
        "action": action,
        "kantian_humanity_principle": result1,
        "utilitarian_principle": result2,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"Evaluation saved to: {output_path}")