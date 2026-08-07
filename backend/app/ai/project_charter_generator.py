import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.project_charter import ProjectCharter


load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from the .env file")

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a senior Project Manager and PMO specialist.

Create a professional Project Charter using only the supplied structured BRD analysis.

Rules:
1. Do not invent business facts that are not supported by the analysis.
2. Convert the available BRD information into a concise, executive-ready charter.
3. Use an empty list or empty string when information is unavailable.
4. Keep milestones realistic but high-level.
5. Do not assign dates unless dates are explicitly available.
6. Preserve project scope, risks, assumptions, dependencies, and stakeholders.
7. Return the result using the required structured output schema.
"""


def generate_project_charter(
    brd_analysis: dict,
) -> ProjectCharter:
    if not brd_analysis:
        raise ValueError("BRD analysis cannot be empty")

    completion = client.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Generate a Project Charter from this BRD analysis:\n\n"
                    + json.dumps(
                        brd_analysis,
                        ensure_ascii=False,
                        indent=2,
                    )
                ),
            },
        ],
        response_format=ProjectCharter,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(
            f"Model refused the request: {message.refusal}"
        )

    if message.parsed is None:
        raise ValueError(
            "The model did not return a valid Project Charter"
        )

    return message.parsed