import os
from ethics.cam.semantics import CausalModel
from ethics.cam.principles import (
    KantianHumanityPrinciple, 
    DoNoHarmPrinciple, 
    DoNoInstrumentalHarmPrinciple, 
    UtilitarianPrinciple, 
    DeontologicalPrinciple, 
    GoalFocusedDeontologicalPrinciple, 
    DoubleEffectPrinciple, 
    DoNoInstrumentalHarmPrincipleWithoutIntentions
)

filepaths = ["/mnt/d/source/ethico/ethics_engine/cases/cam/strategic_bomber.json", 
             "/mnt/d/source/ethico/ethics_engine/cases/cam/terror_bomber.json"]

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
    
    