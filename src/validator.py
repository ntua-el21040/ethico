from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import json

class CausalAgencyModel(BaseModel):
    description: Optional[str] = "No Description"
    actions: list[str]
    background: Optional[list[str]] = []
    consequences: Optional[list[str]] = []
    mechanisms: Optional[dict[str, str]] = {}
    utilities: Optional[dict[str, float]] = {}
    intentions: Optional[dict[str, list[str]]] = {}
    goals: Optional[dict[str, list[str]]] = {}
    patients: Optional[list[str]] = []
    affects: Optional[dict[str, list[list[str]]]] = {}

    @field_validator("actions")
    @classmethod
    def actions_not_empty(cls, v):
        if not v:
            raise ValueError("actions must contain at least one action")
        return v
    

