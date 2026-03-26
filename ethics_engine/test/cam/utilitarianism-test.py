import os
import json
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import UtilitarianPrinciple 

print("Starting Utilitarianism evaluation tests...")

folder_path = "/mnt/d/source/ethico/ethics_engine/cases/cam/utilitarian-test-cases"

for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    if not os.path.isfile(filepath):
        print(f"{filepath} not found")
        
    print("\n" + "="*40)
    print(f"Model: {filename}")
    print("="*40)

    with open(filepath, 'r') as f:
        model = json.load(f)
    
    action = [a for a in model["actions"] if a!="refrain"][0]
    background = model["background"]

    action_world = {action:1, "refrain":0}
    inaction_world = {action:0, "refrain":1}
    for b in background:
        action_world[b] = 1
        inaction_world[b] = 1
        
    action_situation = CausalModel(filepath, action_world)
    inaction_situation = CausalModel(filepath, inaction_world)
    action_situation.alternatives.append(inaction_situation)
    inaction_situation.alternatives.append(action_situation)    
    
    permissibility = action_situation.evaluate(UtilitarianPrinciple)
    print("Utilitarian permissibility of action: ", permissibility)
    
    permissibility = inaction_situation.evaluate(UtilitarianPrinciple)
    print("Utilitarian permissibiliity of inaction: ", permissibility)