import json

def load_checkpoint(path="core/zafira_checkpoint.json"):
    with open(path, "r") as f:
        return json.load(f)

