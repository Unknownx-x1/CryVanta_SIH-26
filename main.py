from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
from pathlib import Path

from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

print("API key found:", os.getenv("OPENROUTER_API_KEY") is not None)

MODEL = "google/gemma-4-26b-a4b-it:free"


@app.post("/narrate")
def narrate(decision: dict):

    prompt = f"""
You are the PredictFuse safety narration assistant.

Your job is to explain the complete system decision to an operator.

IMPORTANT RULES:
- Use ONLY information explicitly provided in the JSON.
- Mention ALL relevant fields provided in the JSON.
- Do not omit important values such as zone, current temperature,
  projected temperature, time to threshold, risk, action,
  vial information, fuse information, route information, or other
  fields if they are present.
- Never invent missing values.
- Never make safety decisions yourself.
- Never issue or recommend physical commands.
- The action in the JSON is already the decision made by the system.
- Explain the information naturally instead of simply reading the JSON.
- Keep the explanation concise but complete, around 3-5 sentences.

Decision data:
{decision}
"""


    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a pharmaceutical cold-chain monitoring narrator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "narration": response.choices[0].message.content
        }

    except Exception:
        return {
            "narration": fallback_narration(decision)
        }


def fallback_narration(d):
    return (
        f"Zone {d.get('zone')} is at {d.get('risk')} risk. "
        f"Current temperature is {d.get('current_temp')}°C. "
        f"Action: {d.get('action')}."
    )