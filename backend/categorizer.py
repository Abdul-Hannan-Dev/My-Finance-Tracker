import os
import requests
from hashlib import md5

class Categorizer:
    def __init__(self):
        self.uclassify_read_key = os.getenv("UCLASSIFY_READ_KEY")
        self.model_name = "Topics"
        self.base_url = "https://api.uclassify.com/v1/uClassify"
        self.hf_api = os.getenv("HF_API_KEY")

    def rule_based(self, description: str) -> str:
        desc = description.lower()
        if any(x in desc for x in ["uber", "bus", "taxi"]):
            return "Travel"
        if any(x in desc for x in ["mcdonald", "kfc", "pizza", "restaurant"]):
            return "Food"
        if any(x in desc for x in ["bill", "electricity", "water", "gas"]):
            return "Utilities"
        if any(x in desc for x in ["netflix", "spotify", "cinema"]):
            return "Entertainment"
        return "Other"

    def ai_based(self, description: str) -> str:
        if self.uclassify_read_key:
            try:
                resp = requests.post(
                    f"{self.base_url}/{self.model_name}/classify",
                    headers={
                        "Authorization": f"Token {self.uclassify_read_key}",
                        "Content-Type": "application/json",
                    },
                    json={"texts": [description]},
                    timeout=5
                )
                data = resp.json()
                best_class = max(data[0]["classification"], key=lambda x: x["p"])["className"]
                return best_class
            except Exception:
                pass

        if self.hf_api:
            try:
                headers = {"Authorization": f"Bearer {self.hf_api}"}
                payload = {"inputs": description}
                resp = requests.post(
                    "https://api-inference.huggingface.co/models/roberta-large-mnli",
                    headers=headers, json=payload, timeout=5
                )
                result = resp.json()
                if isinstance(result, list) and result:
                    labels = {r['label']: r['score'] for r in result}
                    best_label = max(labels, key=labels.get)
                    return best_label
            except Exception:
                pass

        return self.rule_based(description)

    def categorize(self, description: str) -> str:
        return self.ai_based(description)
