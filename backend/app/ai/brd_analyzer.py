import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.brd_analysis import BRDAnalysis


load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from the .env file")

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a senior Business Analyst and PMO specialist.

Analyze the supplied Business Requirements Document and extract only
information that is explicitly stated or strongly supported by the document.

Rules:
1. Do not invent requirements, risks, stakeholders, assumptions, or scope.
2. Use an empty list when information is missing.
3. Keep requirement descriptions clear and concise.
4. Preserve requirement IDs and priorities when provided.
5. Preserve risk likelihood, impact, and mitigation when provided.
6. Return results using the required structured output schema.
"""


def analyze_brd(document_text: str) -> BRDAnalysis:
    if not document_text.strip():
        raise ValueError("Document text cannot be empty")

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
                    "Analyze the following Business Requirements Document:\n\n"
                    f"{document_text}"
                ),
            },
        ],
        response_format=BRDAnalysis,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(f"Model refused the request: {message.refusal}")

    if message.parsed is None:
        raise ValueError("The model did not return a valid BRD analysis")

    return message.parsed