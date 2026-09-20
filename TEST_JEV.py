import os
import json
import requests
from dotenv import load_dotenv

# 读取 .env
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/alpha/decisions"

payload = {
    "model": "typesafe/jev-1.13",

    # 给 JEV 一段信息
    "state": {
        "description": "A person is choosing what to eat for lunch.",
        "weather": "hot",
        "budget": "low",
        "preference": "likes Asian food"
    },

    # 让 JEV 做一个 choice
    "questions": {
        "lunch_choice": {
            "type": "choice",
            "instructions": "Choose the most suitable lunch option for this person.",
            "criteria": {
                "pizza": "The person chooses pizza.",
                "sushi": "The person chooses sushi.",
                "salad": "The person chooses salad."
            }
        }
    }
}

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=60
)

print("HTTP status:", response.status_code)

if response.ok:
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print(response.text)