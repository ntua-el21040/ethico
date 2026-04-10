import os
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import (
    DoubleEffectPrinciple, 
)

folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "cam")
filepaths = [os.path.join(folder_path, "strategic_bomber.json"), 
             os.path.join(folder_path, "terror_bomber.json")]

for filepath in filepaths:
    if not os.path.isfile(filepath):
        print(f"{filepath} not found")
        
    print("\n" + "="*40)
    print(f"Reading file: {filepath}")
    print("="*40)

    # Initialize the Situation with the current file in the loop
    world = {"bomb":1, "refrain":0}
    situation = CausalModel(filepath, world)
    
    permitted = situation.evaluate(DoubleEffectPrinciple)
    print(f"DoubleEffectPrinciple, {permitted}")
    
    