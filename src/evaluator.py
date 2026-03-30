import json
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import UtilitarianPrinciple

# Current version only evaluates based on the UtilitarianPrinciple
def evaluate_dilemma():
    data_dir = "/mnt/d/source/ethico/data"
    situation_path = data_dir + "/situation.json"
    output_path = data_dir + "/evaluation.json"
    with open(situation_path, 'r') as f:
        model = json.load(f)

    action = [a for a in model["actions"] if a!="refrain"][0]
    action_world = {action:1, "refrain":0}
    inaction_world = {action:0, "refrain":1}
    
    action_situation = CausalModel(situation_path, action_world)
    inaction_situation = CausalModel(situation_path, inaction_world)
    action_situation.alternatives.append(inaction_situation)
    inaction_situation.alternatives.append(action_situation)    

    result = action_situation.explain(UtilitarianPrinciple)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"Evaluation saved to: {output_path}") 