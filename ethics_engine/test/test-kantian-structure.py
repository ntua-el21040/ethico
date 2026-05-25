import json
import os
import pytest
from src.validator import KantianModel

folder_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cases",
)


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


@pytest.mark.parametrize("file_path", get_dilemma_files())
def test_kantian_model_validation(file_path):
    """
    Validates the kantian model for each json file.
    """
    with open(file_path, "r") as f:
        model_data = json.load(f)
    KantianModel.model_validate(model_data)
