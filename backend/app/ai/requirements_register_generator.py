import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.requirements_register import RequirementsRegister


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_requirements_register(
    brd_analysis: dict,
) -> RequirementsRegister:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate a Requirements Register."
        )

    system_prompt = """
You are a senior Business Analyst, Project Manager, PMO Lead,
and Requirements Management specialist.

Generate a professional Requirements Register from the supplied
structured BRD analysis.

Requirements:

1. Include every requirement available in the supplied analysis.

2. Preserve existing requirement IDs such as:
   BR-01
   BR-02
   NFR-01
   NFR-02

3. Do not invent requirement IDs when an ID already exists.

4. Classify each requirement using one of:
   Business
   Functional
   Non-Functional
   Security
   Data
   Integration
   Reporting
   Other

5. Preserve the requirement priority from the analysis.

6. Preserve the actual implementation status from the BRD context.
   Do not mark planned requirements as complete.

7. Use only these status values:
   Complete
   Partially Complete
   Planned
   In Progress
   On Hold
   Cancelled

8. Use "Naresh Yeligeti" as owner when the analysis identifies him
   as the project owner, project manager, product owner, or developer.

9. Include test references where supported by the source analysis.
   Do not invent test IDs that are not supported.

10. Include acceptance criteria from the analysis where available.

11. Include dependencies only when supported by the analysis.

12. total_requirements must equal the number of items.

13. complete_count must equal the number of items with status Complete.

14. planned_count must equal the number of items with status Planned.

15. partially_complete_count must equal the number of items with
    status Partially Complete.

16. Set artifact_status to Draft.

17. Return only validated structured output.
"""

    user_prompt = f"""
Create a complete Requirements Register from this structured BRD analysis:

{brd_analysis}
"""

    completion = client.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format=RequirementsRegister,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid Requirements Register."
        )

    return parsed_result