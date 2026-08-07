import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.wbs import WorkBreakdownStructure


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_wbs(
    brd_analysis: dict,
) -> WorkBreakdownStructure:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate a WBS."
        )

    system_prompt = """
You are a senior Project Manager, PMO Lead, Business Analyst,
and Work Breakdown Structure specialist.

Generate a professional, deliverable-based Work Breakdown Structure
from the supplied structured BRD analysis.

Requirements:

1. Use a hierarchical WBS numbering structure such as:
   1
   1.1
   1.1.1
   2
   2.1

2. Use these hierarchy levels:
   Level 1: Project phase
   Level 2: Deliverable
   Level 3: Work package or task

3. Include both completed and planned project work.

4. Preserve the actual project status from the BRD analysis.
   Do not mark planned work as complete.

5. Use only information supported by the supplied analysis.
   Do not invent client requirements, dates, systems, or stakeholders.

6. Assign the owner using a known person or role.
   Use "Naresh Yeligeti" where the analysis clearly identifies
   him as the owner or developer.

7. Add realistic effort estimates in hours for work that remains.
   For completed work, estimate the effort required to deliver it.

8. Include acceptance criteria for deliverables and work packages.

9. Include dependencies using WBS IDs where reasonably possible.

10. The total estimated effort must approximately match the sum
    of the individual item effort estimates.

11. Use these allowed status values:
    Complete
    In Progress
    Planned
    On Hold

12. Use these allowed item types:
    Phase
    Deliverable
    Work Package
    Task

13. Keep the WBS suitable for a portfolio-ready enterprise MVP.

14. Return only the validated structured output.
"""

    user_prompt = f"""
Create a complete Work Breakdown Structure from this structured
BRD analysis:

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
        response_format=WorkBreakdownStructure,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid WBS."
        )

    return parsed_result