import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.raci_matrix import RACIMatrix


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_raci_matrix(
    brd_analysis: dict,
    stakeholder_register: dict | None = None,
    wbs: dict | None = None,
) -> RACIMatrix:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate "
            "a RACI Matrix."
        )

    system_prompt = """
You are a senior Project Manager, PMO Lead, Business Analyst,
Delivery Manager, and Governance specialist.

Generate a professional RACI Matrix for the supplied project.

Use the BRD analysis as the primary source. Use the Stakeholder
Register and WBS when supplied.

Rules:

1. Use only activities, deliverables, decisions, and stakeholders
   supported by the supplied project information.

2. Do not invent named individuals, departments, vendors, or
   contact details.

3. Preserve stakeholder names and stakeholder groups from the
   Stakeholder Register when available.

4. Use activity IDs in this format:
   RAC-001, RAC-002, RAC-003

5. Include important end-to-end activities covering:
   initiation, planning, analysis, design, development, testing,
   deployment, governance, operations, and artifact delivery,
   where supported by the project scope.

6. Each activity must have at least one Responsible stakeholder.

7. Each activity must have exactly one Accountable stakeholder.

8. A stakeholder may be both Responsible and Accountable for an
   activity when this is justified by the single-owner project
   structure.

9. Avoid assigning every stakeholder to every activity.

10. Use these phase values:
    Initiation
    Planning
    Analysis
    Design
    Development
    Testing
    Deployment
    Governance
    Operations
    Other

11. Use these status values:
    Planned
    In Progress
    Complete
    On Hold
    Cancelled
    TBD

12. Reflect the current project status accurately:
    completed backend and artifact work may be Complete;
    active work may be In Progress;
    future frontend, authentication, deployment, and advanced
    features should be Planned.

13. Use Naresh Yeligeti as Responsible and Accountable where the
    project information shows he is the sole developer, project
    manager, product owner, or business owner.

14. Use Mentor as Consulted for architecture, technical design,
    maintainability, or critical implementation decisions when
    supported.

15. Use Portfolio Reviewer / Interviewer as Informed or Consulted
    only for portfolio review, demo, and milestone validation
    activities.

16. Use Future End User as Consulted or Informed for usability,
    artifact validation, future UI, and workflow-related
    activities.

17. total_activities must equal the number of activities.

18. stakeholders must contain only unique stakeholder names used
    in the matrix.

19. Set artifact_status to Draft.

20. Return only validated structured output.
"""

    user_prompt = f"""
Create a complete RACI Matrix from the following project data.

BRD analysis:
{brd_analysis}

Stakeholder Register:
{stakeholder_register or {}}

WBS:
{wbs or {}}
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
        response_format=RACIMatrix,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid RACI Matrix."
        )

    return parsed_result