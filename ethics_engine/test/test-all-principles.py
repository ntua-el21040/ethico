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

folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "cam")

for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    if not os.path.isfile(filepath):
        print(f"{filepath} not found")
        
    print("\n" + "="*40)
    print(f"Reading file: {filepath}")
    print("="*40)

    # Initialize the Situation with the current file in the loop
    sit = CausalModel(filepath)

    perm = sit.evaluate(DeontologicalPrinciple)
    print("DeontologicalPrinciple: ", perm)

    perm = sit.evaluate(GoalFocusedDeontologicalPrinciple)
    print("GoalFocusedDeontologicalPrinciple: ", perm)

    perm = sit.evaluate(KantianHumanityPrinciple)
    print("KantianHumanityPrinciple: ", perm)

    perm = sit.evaluate(DoNoHarmPrinciple)
    print("DoNoHarmPrinciple: ", perm)

    perm = sit.evaluate(DoNoInstrumentalHarmPrinciple)
    print("DoNoInstrumentalHarmPrinciple: ", perm)

    perm = sit.evaluate(UtilitarianPrinciple)
    print("UtilitarianPrinciple: ", perm)

    perm = sit.evaluate(DoubleEffectPrinciple)
    print("DoubleEffectPrinciple: ", perm)

    perm = sit.evaluate(DoNoInstrumentalHarmPrincipleWithoutIntentions)
    print("DoNoInstrumentalHarmPrincipleWithoutIntentions: ", perm)