import ast
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class CausalAgencyModel(BaseModel):
    """
    Schema for HERA Causal Agency Models (CAM).
    Matches what CausalModel.__init__ in ethics/cam/semantics.py reads.

    Conceptually: a CAM describes a situation in terms of
    - actions:      what the agent can do (exogenous variables)
    - background:   facts true independent of the agent (exogenous variables)  
    - consequences: facts determined by the causal structure (endogenous variables)
    - mechanisms:   structural equations defining how consequences are determined
    - utilities:    moral value of consequences
    - intentions:   what the agent intends when performing each action
    - goals:        what the agent aims to bring about with each action
    - patients:     persons who can be treated as means or ends (for Kantian reasoning)
    - affects:      which consequences positively/negatively affect which patients
    """

    description: Optional[str] = "No Description"
    
    actions: list[str]
    """
    The agent's available actions. These are exogenous variables —
    their truth value is set externally via the 'world' argument to CausalModel.
    At least one is required. The action being evaluated is set to 1/True,
    all others to 0/False.
    Example: ["pull", "refrain"]
    """

    background: list[str] = []
    """
    Facts that hold independently of the agent's actions.
    Also exogenous — their values are fixed in the world dict.
    Example: ["tram_approaching", "five_on_track"]
    """

    consequences: list[str] = []
    """
    Facts whose truth value is determined by the structural equations
    in 'mechanisms'. These are endogenous variables — the causal model
    computes their values from the exogenous variables.
    Example: ["person1_dies", "person2_dies"]
    """

    mechanisms: dict[str, str] = {}
    """
    Structural equations. Each key is a consequence name (must be in
    'consequences'). Each value is a Python expression string that
    HERA will eval() to build a formula object.

    Allowed constructs:
      - Quoted atom names:          "'action_name'"  or  "'consequence_name'"
      - Logical connectives:        And(...), Or(...), Not(...)
      - Combinations:               "Or('pull', And('background_fact', 'c1'))"

    The formula is evaluated in terms of other actions, background facts,
    and other consequences. The causal model solves for consistent truth
    values across all structural equations simultaneously.

    Example:
      {"person1_dies": "Not('pull')",
       "person2_dies": "'pull'"}
    """

    # --- Moral/evaluative structure ---

    utilities: dict[str, float] = {}
    """
    Moral utility of consequences (and their negations).
    Keys are atom strings as they appear in the formula language.
    Both positive and negative literals can have utilities.
    Positive values = good outcomes, negative = bad outcomes.

    Example:
      {"person1_dies": -5,
       "Not('person1_dies')": 5,
       "person2_dies": -1,
       "Not('person2_dies')": 1}

    Used by: UtilitarianPrinciple, DoubleEffectPrinciple.
    """

    intentions: dict[str, list[str]] = {}
    """
    What the agent intends when performing each action.
    Keys are action names (must be in 'actions').
    Values are lists of consequence strings the agent intends,
    including the action itself.

    Example:
      {"pull": ["pull", "Not('person1_dies')"],
       "refrain": ["refrain"]}

    Used by: IntentionFocusedDeontologicalPrinciple, DoubleEffectPrinciple.
    Note: consequence strings in the list are passed through my_eval(),
    so they can include Not(...) wrapping.
    """

    goals: dict[str, list[str]] = {}
    """
    What the agent aims to bring about with each action.
    Keys are action names (must be in 'actions').
    Values are lists of consequence strings that are the agent's goals.
    Distinct from intentions: goals are the desired end-states,
    intentions include the means taken to get there.

    Example:
      {"pull": ["Not('person1_dies')"],
       "refrain": []}

    Used by: GoalFocusedDeontologicalPrinciple, KantianHumanityPrinciple.
    """

    patients: list[str] = []
    """
    The moral patients in the situation — the persons who can be
    treated as means or ends. Required for Kantian reasoning.

    Example: ["person1", "person2"]

    Used by: KantianHumanityPrinciple (Reading 1 and 2).
    """

    affects: dict[str, list[list[str]]] = {}
    """
    How consequences affect moral patients.
    Keys are consequence strings (atoms or "Not('x')" strings).
    Values are lists of [patient_name, sign] pairs where sign is "+" or "-".
    "+" = this consequence positively affects this patient.
    "-" = this consequence negatively affects this patient.
    An empty list [] means the consequence affects no one.

    Example:
      {"person1_dies":       [["person1", "-"]],
       "Not('person1_dies')": [["person1", "+"]],
       "person2_dies":       [["person2", "-"]],
       "pull":               []}

    Used by: KantianHumanityPrinciple, AffectsPos, AffectsNeg.
    """

    @field_validator("actions")
    @classmethod
    def actions_not_empty(cls, v):
        if not v:
            raise ValueError("actions must contain at least one action")
        return v
    

