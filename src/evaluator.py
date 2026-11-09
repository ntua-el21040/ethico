import os
import json
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import KantianHumanityPrinciple, UtilitarianPrinciple


def evaluate_dilemma(situation_path: str, evaluation_path: str):
    """
    Reads a dilemma from the specified situation path and evaluates it using the Kantian Humanity Principle 
    and the Utilitarian Principle. The results are saved to the specified evaluation path.
    The dilemma is always assumed to be valid.
    """
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
    
    with open(evaluation_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"Evaluation saved to: {evaluation_path}")