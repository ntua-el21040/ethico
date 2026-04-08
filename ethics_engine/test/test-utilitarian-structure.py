import json
import os
import pytest
from src.validator import UtilitarianModel

DILEMMA_DIR = "/mnt/d/source/ethico/ethics_engine/cases/cam"

def get_dilemma_files():
    """
    Helper function to gather all JSON files from the DILEMMA_DIR.
    """
    files = []
    if os.path.exists(DILEMMA_DIR):
        for filename in os.listdir(DILEMMA_DIR):
            if filename.endswith(".json"):
                files.append(os.path.join(DILEMMA_DIR, filename))
    return files

def check_structure(situation_path):
    """
    Validates a single JSON file against the UtilitarianModel.
    """
    with open(situation_path, 'r') as f:
        model_data = json.load(f)
    return UtilitarianModel.model_validate(model_data)

@pytest.mark.parametrize("file_path", get_dilemma_files())
def test_utilitarian_model_validation(file_path):
    """
    Test case that iterates through each file found in DILEMMA_DIR.
    The filename is used in the test ID for better reporting.
    """
    try:
        check_structure(file_path)
    except Exception as e:
        pytest.fail(f"Validation failed for {os.path.basename(file_path)}: {e}")