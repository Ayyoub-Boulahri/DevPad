import json

class ProfileStore:
    def __init__(self):
        self.profiles = []

    def load_json(self, raw: str):
        data = json.loads(raw)
        self.profiles = data.get("profiles", [])

    def to_json(self) -> str:
        return json.dumps({"profiles": self.profiles}, indent=2)

    def add_profile(self, name: str):
        self.profiles.append({"name": name, "actions": []})

    def delete_profile(self, index: int):
        self.profiles.pop(index)

    def add_action(self, profile_index: int, action: dict):
        self.profiles[profile_index]["actions"].append(action)

    def delete_action(self, profile_index: int, action_index: int):
        self.profiles[profile_index]["actions"].pop(action_index)

    def rename_profile(self, index: int, name: str):
        self.profiles[index]["name"] = name