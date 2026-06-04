import pytest
import json
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import UtilitarianPrinciple
import os

GROUND_TRUTH = {
    "atom_bomb_trolley.json": True,
    "disclose_burglar.json": False,
    "disclose_doctor.json": True,
    "fatman_trolley_problem.json": True,
    "flowers_permissible.json": True,
    "flowers.json": True,
    "hijacked_dilemma.json": True,
    "indianer.json": True,
    "lying_robot.json": True,
    "mixed_trolley.json": True,
    "slice_patch.json": False,
    "strategic_bomber.json": True,
    "terror_bomber.json": True,
    "trolley_problem_permissible.json": True,
    "trolley_problem.json": True,
    "suffering.json": False,
    "sadism.json": False,
    "drugs.json": False
}

folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "cases")


def evaluate(situation_path):
    with open(situation_path, 'r') as f:
        model = json.load(f)

    action = [a for a in model["actions"] if a != "refrain"][0]
    action_world = {action: 1, "refrain": 0}
    inaction_world = {action: 0, "refrain": 1}

    action_situation = CausalModel(situation_path, action_world)
    inaction_situation = CausalModel(situation_path, inaction_world)
    action_situation.alternatives.append(inaction_situation)
    inaction_situation.alternatives.append(action_situation)

    return action_situation.evaluate(UtilitarianPrinciple)


@pytest.mark.parametrize("filename, expected", GROUND_TRUTH.items())
def test_utilitarian_verdict(filename, expected):
    """
    Tests only the files defined in GROUND_TRUTH. 
    Constructs the path using basic string concatenation.
    """
    path = os.path.join(folder_path, filename)
    
    if not os.path.exists(path):
        pytest.fail(f"Dilemma file missing: {path}")

    result = evaluate(path)
    assert result == expected, (
        f"{filename}: expected permissible={expected}, got {result}"
    )