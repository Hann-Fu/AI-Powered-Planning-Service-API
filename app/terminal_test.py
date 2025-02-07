from moderation import check_policy
from further_info_analyzer import get_further_info_fc_pydantic_schema
from final_plan_generator import get_final_plan
from time_series_tasks_generator import get_time_series_data_tool_call


def get_user_goal() -> str:
    goal = input("Enter your goal or idea: ")
    plan = input("Enter your plan(optional, could be empty): ")
    return goal, plan

def get_user_further_details(info_needed: list) -> list:

    details = []
    for info in info_needed:
        # Prompt the user based on the guide provided in each info requirement
        user_input = input(f"Provide details for '{info.keyword}' (Guide: {info.guide}): ")
        details.append({"keyword": {info.keyword}, "details": user_input})
    return details

def main():
    # Step 1: Ask for the user's goal.

    user_goal, user_plan = get_user_goal()


    # Step 2: Check if the user's input conflicts with policies.
    if not check_policy(user_goal, user_plan):
        print("Your input conflicts with our policies. Please modify your goal.")
        return

    # Step 3: Use function calling to determine further information needed.
    try:
        further_info = get_further_info_fc_pydantic_schema(user_goal, user_plan)
    except Exception as e:
        print("Error during further information analysis:", e)
        return

    # Step 3-2: Ask the user to provide the required further details.
    info_needed_list = get_user_further_details(further_info.info_needed)

    # Step 4: Build and generate the final tailored plan.
    try:
        final_plan = get_final_plan(user_goal, info_needed_list)
        print("Final Plan:", final_plan)
    except Exception as e:
        print("Error during final plan generation:", e)
        return

    # Step 5: Generate time series data based on the final plan.
    try:
        time_series_plan = get_time_series_data_tool_call(user_goal, user_plan, further_info, final_plan)
        print("Time Series Data:", time_series_plan)
    except Exception as e:
        print("Error during time series data generation:", e)


if __name__ == "__main__":
    main()
