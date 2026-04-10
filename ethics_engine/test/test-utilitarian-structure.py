import json
import os
import pytest
from src.validator import UtilitarianModel

folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "cam")

def get_dilemma_files():
    """
    Helper function to gather all JSON files from the folder_path.
    """
    files = []
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                files.append(os.path.join(folder_path, filename))
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
    Test case that iterates through each file found in folder_path.
    The filename is used in the test ID for better reporting.
    """
    try:
        check_structure(file_path)
    except Exception as e:
        pytest.fail(f"Validation failed for {os.path.basename(file_path)}: {e}")