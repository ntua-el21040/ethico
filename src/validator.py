from typing import Optional
from pydantic import BaseModel, field_validator, ValidationInfo


class UtilitarianModel(BaseModel):
    description: str
    actions: list[str]
    consequences: list[str]
    mechanisms: dict[str, str]
    utilities: dict[str, int]

    @field_validator("actions")
    @classmethod
    def validate_actions(cls, actions: list[str]) -> list[str]:
        if len(actions) != 2:
            raise ValueError("'actions' must contain exactly two actions.")
        if "refrain" not in actions:
            raise ValueError("'actions' must contain a 'refrain' action.")
        return actions
    
    @field_validator("consequences")
    @classmethod
    def validate_consequences(cls, consequences: list[str]) -> list[str]:
        if len(consequences) == 0:
            raise ValueError("'consequences' must contain at least one consequence.")
        return consequences

    @field_validator("mechanisms")
    @classmethod
    def validate_mechanisms(cls, mechanisms: dict[str, str], info: ValidationInfo) -> dict[str, str]:
        actions = info.data['actions']
        consequences = info.data['consequences']

        for key in mechanisms.keys():
            if key not in consequences and not (key.startswith("Not('") and key.endswith("')")):
                raise ValueError(f"Mechanism key '{key}' must be a consequence or its negation.")
        
        for value in mechanisms.values():
            if value.startswith("Not('") and value.endswith("')"):
                extracted_val = value[5:-2]
            elif value.startswith("'") and value.endswith("'"):
                extracted_val = value[1:-1]
            else:
                raise ValueError(f"Mechanism value '{value}' must be wrapped in single quotes.")

            if extracted_val not in actions and extracted_val not in consequences:
                raise ValueError(f"Mechanism value '{value}' contains '{extracted_val}', which is not a defined action or consequence.")
        
        for consequence in consequences:
            negation = f"Not('{consequence}')"
            if consequence not in mechanisms and negation not in mechanisms:
                raise ValueError(f"Each consequence must have a corresponding mechanism key or its negation.")
        return mechanisms

    @field_validator("utilities")
    @classmethod
    def validate_utilities(cls, utilities: dict[str, int], info: ValidationInfo) -> dict[str, int]:
        consequences = info.data["consequences"]
        negations = {f"Not('{consequence}')" for consequence in consequences}
        
        for key in utilities.keys():
            if key not in consequences and key not in negations:
                raise ValueError(f"Utility key '{key}' must be a consequence or its negation.")
        
        for consequence in consequences:
            if f"'{consequence}'" not in utilities and f"Not('{consequence}')" not in utilities:
                raise ValueError(f"Each consequence or its negation must have a corresponding utility key.")
        return utilities


class CausalAgencyModel(BaseModel):
    description: Optional[str] = "Description of the moral dilemma"
    actions: list[str]
    consequences: list[str] = []
    mechanisms: dict[str, str] = {}
    utilities: dict[str, int] = {}
    intentions: dict[str, list[str]] = {}
    goals: dict[str, list[str]] = {}
    patients: list[str] = []
    affects: dict[str, list[list[str]]] = {}
    
    
    
response_schema = {
    "type": "object",
    "required": ["description", "actions", "consequences", "mechanisms", "utilities"],
    "properties": {
        "description": {
            "type": "string"
        },
        "actions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "consequences": {
            "type": "array",
            "items": {"type": "string"}
        },
        "mechanisms": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "utilities": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}