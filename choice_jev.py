import os
import time
import random
import requests
from dotenv import load_dotenv
from requests.exceptions import SSLError, ConnectionError, Timeout, HTTPError

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/alpha/decisions"


def ask_jev(state, questions, max_retries=6, timeout=180):

    payload = {
        "model": "typesafe/jev-1.13",
        "state": state,
        "questions": questions
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Connection": "close"
    }

    for attempt in range(1, max_retries + 1):

        try:
            response = requests.post(
                URL,
                headers=headers,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == max_retries:
                    response.raise_for_status()

                wait_time = min(
                    2 ** attempt + random.uniform(0, 1),
                    60
                )

                print(
                    f"HTTP {response.status_code}, "
                    f"retry {attempt}/{max_retries} "
                    f"after {wait_time:.1f}s"
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except (SSLError, ConnectionError, Timeout) as e:

            if attempt == max_retries:
                raise

            wait_time = min(
                2 ** attempt + random.uniform(0, 1),
                60
            )

            print(
                f"{type(e).__name__}: retry "
                f"{attempt}/{max_retries} "
                f"after {wait_time:.1f}s"
            )

            time.sleep(wait_time)

        except HTTPError:
            raise