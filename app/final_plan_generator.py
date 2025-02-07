from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

def get_final_plan(user_goal: str, user_details: list) -> str:
    # Construct the final prompt by combining the user’s original goal and further details.
    combined_details = "\n".join(
        [f"{detail['keyword']}: {detail['details']}" for detail in user_details]
    )


    prompt_text = ("According to the following information, generate a tailored plan."
                    f"User's original goal: {user_goal}"
                    f"Additional details:{combined_details}")

    messages = [
        SystemMessage(content="You are a helpful planner that creates a comprehensive, detailed plan in markdown format for user by provided information."),
        HumanMessage(content=prompt_text)
    ]

    model = ChatOpenAI(model_name="gpt-4o", temperature=1.0)
    response = model.invoke(
        messages,
        top_p=0.95,
        temperature=1.02,
    )
    final_plan = response.content

    return final_plan