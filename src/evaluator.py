from ethics.plans.semantics import Situation
from ethics.plans.principles import KantianHumanity, Utilitarianism, DoNoHarm
import json
from pathlib import Path


data_dir = Path.cwd() / "data"
situation_path = data_dir / "situation.json"
output_path = data_dir / "evaluation.json"

situation = Situation(str(situation_path))

principles = [
    KantianHumanity,
    Utilitarianism,
    DoNoHarm
]

evaluations = {}

for principle in principles:
    evaluations[principle.__name__] = situation.evaluate(principle)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(evaluations, f, indent=2)

print(f"Evaluation saved to: {output_path}")
 