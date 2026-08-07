import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.raid_risk_register import RAIDAndRiskRegister


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_raid_and_risk_register(
    brd_analysis: dict,
) -> RAIDAndRiskRegister:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate the RAID Log "
            "and Risk Register."
        )

    system_prompt = """
You are a senior Project Manager, PMO Lead, Risk Manager,
Business Analyst, and Delivery Governance specialist.

Generate a professional RAID Log and Risk Register from the
supplied structured BRD analysis.

Rules:

1. Use only information supported by the supplied analysis.

2. Create RAID items for:
   - Risks
   - Assumptions
   - Issues
   - Dependencies

3. Use these RAID ID formats:
   - Risk: R-001, R-002
   - Assumption: A-001, A-002
   - Issue: I-001, I-002
   - Dependency: D-001, D-002

4. Each risk appearing in the RAID Log must also appear in the
   Risk Register using the same risk ID.

5. Do not create duplicate risks.

6. Use "Naresh Yeligeti" as owner when the analysis identifies
   him as project owner, project manager, product owner,
   developer, or responsible delivery lead.

7. Use only these RAID statuses:
   Open
   In Progress
   Monitoring
   Resolved
   Accepted
   Closed
   Planned

8. Use only these Risk Register statuses:
   Open
   In Progress
   Monitoring
   Accepted
   Mitigated
   Closed
   Realized

9. Probability must be:
   High
   Medium
   Low

10. Impact must be:
    Critical
    High
    Medium
    Low

11. Priority must be:
    Critical
    High
    Medium
    Low

12. Calculate risk_score using:
    Probability:
      High = 5
      Medium = 3
      Low = 1

    Impact:
      Critical = 5
      High = 4
      Medium = 3
      Low = 1

    risk_score = probability score multiplied by impact score.

13. Set risk priority using:
    20-25 = Critical
    12-19 = High
    6-11 = Medium
    1-5 = Low

14. Do not invent dates. Leave due_date and target_date blank
    when no supported date exists.

15. Include mitigation plans supported by the analysis.

16. Include contingency plans only when reasonable and directly
    related to the identified risk.

17. Include an early warning trigger for each risk.

18. Source references should use relevant requirement,
    assumption, dependency, risk, scope, or analysis references.

19. total_raid_items must equal the number of raid_items.

20. total_risks must equal the number of risk_register items.

21. open_risk_count must equal risks with status:
    Open
    In Progress
    Monitoring
    Accepted

22. high_priority_risk_count must equal risks with priority:
    Critical
    High

23. Set artifact_status to Draft.

24. Return only validated structured output.
"""

    user_prompt = f"""
Create a complete RAID Log and Risk Register from this structured
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
        response_format=RAIDAndRiskRegister,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid RAID Log "
            "and Risk Register."
        )

    return parsed_result