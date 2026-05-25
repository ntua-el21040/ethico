import os
import json
import pytest
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import KantianHumanityPrinciple, UtilitarianPrinciple

KANTIAN_TRUTH = {
    "trolley_problem.json": False,
    "trolley_problem_permissible.json": True,
    "fatman_trolley_problem.json": False,
    "mixed_trolley.json": True,
    "atom_bomb_trolley.json": True,
    "disclose_burglar.json": True,
    "disclose_doctor.json": True,
    "lying_robot.json": True,
    "indianer.json": False,
    "slice_patch.json": True,
    "flowers.json": False,
    "flowers_permissible.json": True,
    "hijacked_dilemma.json": False,
    "strategic_bomber.json": True,
    "terror_bomber.json": False,
    "suffering.json": True,
    "sadism.json": False,
    "drugs.json": False
}

UTILITARIAN_TRUTH = {
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

folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases")
test_cases = [
    (filename, KANTIAN_TRUTH[filename], UTILITARIAN_TRUTH[filename])
    for filename in KANTIAN_TRUTH.keys()
]

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

    kantian_evaluation = action_situation.evaluate(KantianHumanityPrinciple)
    utilitarian_evaluation = action_situation.evaluate(UtilitarianPrinciple)

    return kantian_evaluation, utilitarian_evaluation


@pytest.mark.parametrize("filename, expected_kantian, expected_utilitarian", test_cases)
def test_theory_verdicts(filename, expected_kantian, expected_utilitarian):
    """
    Tests all files for both Kantian and Utilitarian theories against their ground truths. 
    Constructs the path using basic string concatenation.
    """
    path = os.path.join(folder_path, filename)
    
    if not os.path.exists(path):
        pytest.fail(f"Dilemma file missing: {path}")

    actual_kantian, actual_utilitarian = evaluate(path)
    
    assert actual_kantian == expected_kantian, (
        f"{filename} (Kantian): expected permissible={expected_kantian}, got {actual_kantian}"
    )
    
    assert actual_utilitarian == expected_utilitarian, (
        f"{filename} (Utilitarian): expected permissible={expected_utilitarian}, got {actual_utilitarian}"
    )