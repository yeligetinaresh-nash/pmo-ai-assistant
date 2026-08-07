import os

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.stakeholder_register import StakeholderRegister


load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)


def generate_stakeholder_register(
    brd_analysis: dict,
) -> StakeholderRegister:
    if not brd_analysis:
        raise ValueError(
            "BRD analysis is required to generate "
            "a Stakeholder Register."
        )

    system_prompt = """
You are a senior Project Manager, PMO Lead, Business Analyst,
Change Manager, and Stakeholder Engagement specialist.

Generate a professional Stakeholder Register from the supplied
structured BRD analysis.

Rules:

1. Use only stakeholders supported by the supplied analysis.

2. Preserve named stakeholders when names are available.

3. Use stakeholder groups or role names when individual names
   are not available.

4. Use stakeholder IDs in this format:
   STK-001, STK-002, STK-003

5. Do not create duplicate stakeholders.

6. Use "Naresh Yeligeti" for the project owner, project manager,
   product owner, developer, or delivery lead when supported by
   the analysis.

7. stakeholder_type must be one of:
   Internal
   External
   Vendor
   Customer
   Other

8. interest_level must be:
   High
   Medium
   Low

9. influence_level must be:
   High
   Medium
   Low

10. Determine power_interest_quadrant using:
    High influence + High interest = Manage Closely
    High influence + Medium/Low interest = Keep Satisfied
    Medium/Low influence + High interest = Keep Informed
    Medium/Low influence + Medium/Low interest = Monitor

11. current_engagement and desired_engagement must be:
    Unaware
    Resistant
    Neutral
    Supportive
    Leading

12. communication_frequency must be one of:
    Daily
    Weekly
    Fortnightly
    Monthly
    At Milestones
    As Needed
    Other

13. Do not invent email addresses, phone numbers, or contact data.

14. Include expectations, responsibilities, and communication
    needs only when supported by the analysis or clearly implied
    by the stakeholder's project role.

15. Use project delivery and governance context when assigning
    communication needs and frequency.

16. Use "Naresh Yeligeti" as relationship owner unless another
    owner is explicitly supported.

17. status must be:
    Active
    Planned
    Monitoring
    Inactive
    Closed

18. total_stakeholders must equal the number of stakeholders.

19. high_influence_count must equal stakeholders with influence
    level High.

20. manage_closely_count must equal stakeholders with quadrant
    Manage Closely.

21. Set artifact_status to Draft.

22. Return only validated structured output.
"""

    user_prompt = f"""
Create a complete Stakeholder Register from this structured
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
        response_format=StakeholderRegister,
    )

    parsed_result = completion.choices[0].message.parsed

    if parsed_result is None:
        raise ValueError(
            "The model did not return a valid "
            "Stakeholder Register."
        )

    return parsed_result