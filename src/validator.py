from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

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
            "type": "object"
        },
        "utilities": {
            "type": "object"
        }
    }
}

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

    @field_validator("actions")
    @classmethod
    def validate_actions(cls, v):
        if len(v) < 2:
            raise ValueError("'actions' must contain at least two actions.")
        if "refrain" not in v:
            raise ValueError("'actions' must contain a 'refrain' action.")
        return v
