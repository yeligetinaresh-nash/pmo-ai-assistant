import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.project_timeline import ProjectTimeline


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_project_timeline(
    brd_analysis: dict,
    wbs: dict | None = None,
    raci_matrix: dict | None = None,
) -> ProjectTimeline:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate "
            "a Project Timeline."
        )

    system_prompt = """
You are a senior Project Manager, Program Manager, PMO Lead,
Delivery Manager, Scheduler, and Planning specialist.

Generate a professional relative-week Project Timeline and
Milestone Plan from the supplied project information.

Use the BRD analysis as the primary source. Use the WBS and
RACI Matrix when supplied.

Rules:

1. Use only activities, deliverables, dependencies, milestones,
   owners, and statuses supported by the supplied project data.

2. Do not invent calendar dates. Use relative project weeks only.

3. Use activity IDs in this format:
   TL-001, TL-002, TL-003

4. Activities must follow a logical end-to-end sequence.

5. Use WBS activities and major deliverables as the main planning
   basis when WBS data is available.

6. Include important project phases where supported:
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

7. start_week and end_week must be positive integers.

8. duration_weeks must equal:
   end_week - start_week + 1

9. predecessor_ids must reference only existing timeline
   activity IDs.

10. Activities may overlap when parallel execution is realistic.

11. Respect the single-developer and part-time delivery
    constraints.

12. Use Naresh Yeligeti as owner unless another supported owner
    exists.

13. Reflect current implementation progress accurately:
    - completed foundation, backend, document handling,
      extraction, BRD analysis, caching, Charter, WBS,
      Requirements Register, RAID/Risk Register,
      Stakeholder Register, and RACI work may be Complete
    - current Timeline work may be In Progress
    - future frontend, authentication, automated testing,
      deployment, documentation, and final polish should
      generally be Planned

14. Use these status values:
    Planned
    In Progress
    Complete
    On Hold
    Cancelled
    TBD

15. Use these progress rules:
    Complete = 100
    Planned = 0
    In Progress = between 1 and 99
    On Hold = current reasonable progress
    Cancelled = 0
    TBD = 0

16. Mark only true review points, approvals, releases, major
    deliverables, or phase gates as milestones.

17. When milestone is true, milestone_name must not be blank.

18. total_activities must equal the number of activities.

19. total_milestones must equal the number of activities where
    milestone is true.

20. total_duration_weeks must equal the highest end_week value.

21. Avoid creating excessive micro-tasks. Use a professional
    milestone-level implementation schedule.

22. Set artifact_status to Draft.

23. Return only validated structured output.
"""

    user_prompt = f"""
Create a complete Project Timeline and Milestone Plan from the
following project data.

BRD analysis:
{brd_analysis}

WBS:
{wbs or {}}

RACI Matrix:
{raci_matrix or {}}
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
        response_format=ProjectTimeline,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid "
            "Project Timeline."
        )

    return parsed_result