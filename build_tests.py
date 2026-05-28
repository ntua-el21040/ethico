import os
import json
import glob

# Recursively find all text files in the experiments folder
txt_files = glob.glob('experiments/**/*.txt', recursive=True)

tests = []

for txt_path in txt_files:
    # 1. Get the directory where the current .txt file is located
    dir_name = os.path.dirname(txt_path)
    
    # 2. Point directly to 'situation.json' in that same directory
    json_path = os.path.join(dir_name, "situation.json")
    
    # 3. Skip if the JSON doesn't exist in this specific folder
    if not os.path.exists(json_path):
        print(f"Skipping {txt_path} - No 'situation.json' found in {dir_name}")
        continue
        
    # Read the pre-generated JSON (your system's extraction)
    with open(json_path, 'r', encoding='utf-8') as jf:
        extracted_json_content = jf.read()
    
    # 4. Build the test case
    test_case = {
        "vars": {
            "conversation": f"file://{txt_path}",
            "extracted_json": extracted_json_content
        },
        "assert": [
            {
                "type": "llm-rubric",
                "value": "Evaluate the JSON output. Does it accurately reflect the moral dilemma in this conversation:\n\n{{conversation}}\n\nEnsure the actions, affected entities (patients), and moral trade-offs are correctly captured without hallucinated details."
            }
        ]
    }
    tests.append(test_case)

# Generate the final test suite
with open('tests.json', 'w') as out_file:
    json.dump(tests, out_file, indent=2)

print(f"Success! Generated {len(tests)} evaluation tests in tests.json.")