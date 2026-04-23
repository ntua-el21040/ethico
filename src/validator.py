from typing import Optional
from pydantic import BaseModel, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    anthropic_api_key: str
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
class KantianModel(BaseModel):
    description: str
    actions: list[str]
    consequences: list[str]
    utilities: dict[str, int] = {}
    mechanisms: dict[str, str]
    patients: list[str]
    affects: dict[str, list[list[str]]]
        
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
        actions_negations = {f"Not('{action}')" for action in actions}
        consequences_negations = {f"Not('{consequence}')" for consequence in consequences}
        valid_causes = set(actions) | set(consequences) | actions_negations | consequences_negations

        for consequence, cause in mechanisms.items():
            if consequence not in consequences and not (consequence.startswith("Not('") and consequence.endswith("')")):
                raise ValueError(f"Mechanism key '{consequence}' must be a consequence or its negation.")
            
        for consequence in consequences:
            negation = f"Not('{consequence}')"
            if consequence not in mechanisms and negation not in mechanisms:
                raise ValueError(f"Each consequence must have a corresponding mechanism key or its negation.")
        return mechanisms


    @field_validator("patients")
    @classmethod
    def validate_patients(cls, patients: list[str]) -> list[str]:
        if len(patients) == 0:
            raise ValueError("'patients' must contain at least one patient.")
        return patients
    
    @field_validator("affects")
    @classmethod
    def validate_affects(cls, affects: dict[str, list[list[str]]], info: ValidationInfo) -> dict[str, list[list[str]]]:
        patients = info.data['patients']
        actions = info.data['actions']
        consequences = info.data['consequences']
        
        actions_negations = {f"Not('{action}')" for action in actions}
        consequences_negations = {f"Not('{consequence}')" for consequence in consequences}
        valid_events = set(consequences)  | set(actions) | consequences_negations | actions_negations
        
        for event, affect_list in affects.items():
            if event not in valid_events:
                raise ValueError(f"Affect key '{event}' must be an action or consequence or their negation.")
            for affect in affect_list:
                if len(affect) != 2:
                    raise ValueError(f"Each affect entry must be a list of [patient, valence].")
                patient, valence = affect
                if patient not in patients:
                    raise ValueError(f"Affect patient '{patient}' must be a patient.")
                if valence not in ["+", "-"]:
                    raise ValueError(f"Affect valence must be '+' or '-'.")
        return affects


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
        
        utility_keys = set(utilities.keys())

        for key in utility_keys:
            if key not in consequences and key not in negations:
                raise ValueError(
                    f"Utility key '{key}' must be a consequence or its negation."
                )

        for consequence in consequences:
            if consequence not in utility_keys and f"Not('{consequence}')" not in utility_keys:
                raise ValueError(
                    f"Each consequence or its negation must have a corresponding utility key."
                )
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