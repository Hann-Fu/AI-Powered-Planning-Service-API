from pydantic import BaseModel, Field
from typing import Union
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json
class Ymd(BaseModel):
    date: str = Field(
        description="The date of the task in YYYY-MM-DD format"
    )

class SpecificType(BaseModel):
    specific: list[Ymd] = Field(description="Specify dates for this task")

class OnWorkdayType(BaseModel):
    on_workday: list[int] = Field(
        description=(
            "List of integers representing the weekdays the task should be performed on. "
            "Use 1 for Monday, 2 for Tuesday, ..., up to 5 for Friday. "
            "For example, [1, 2, 3] for Monday to Wednesday, or [3, 5] for Wednesday and Friday."
        )
    )

class OnWeekendType(BaseModel):
    on_weekend: list[int] = Field(
        description=(
            "List of integers representing the weekends the task should be performed on. "
            "Use 1 for Saturday, 2 for Sunday, or [1, 2] for both."
        )
    )

class OnWeekdayType(BaseModel):
    on_weekday: list[int] = Field(
        description=(
            "List of integers representing the weekdays the task should be performed on. "
            "Use 1 for Monday, 2 for Tuesday, ..., up to 5 for Friday. "
            "For example, [1, 2, 3] for Monday to Wednesday, or [3, 7] for Wednesday and Sunday."
        )
    )   

class OnMonthdayType(BaseModel):
    on_monthday: list[int] = Field(
        description=(
            "List of integers representing the monthdays the task should be performed on. "
            "Use 1 for the first day of the month, 2 for the second day, ..., up to 28/29/30/31 for the last day of the month(depends on the month). "
            "For example, [1, 2, 3] for the first three days of the month, or [3, 5] for the third and fifth days of the month."
        )
    )

class PeriodicType(BaseModel): 
    periodic: int = Field(description="Specify the period of the task in days")

class RepeatType(str, Enum):
    SPECIFIC = "Specific"
    EVERYDAY = "Everyday"
    ON_WORKDAY = "On workday"
    ON_WEEKEND = "On Weekend"
    ON_WEEKDAY = "On weekday"
    ON_MONTHDAY = "On monthday"
    PERIODIC = "Periodic"

class Quantization(BaseModel):
    progress_start: int = Field(description="The start progress of the task")
    goal: int = Field(description="The goal of the task")

class AcrossTimeAttribute(BaseModel):
    start_date: str = Field(description="The start date of the task in YYYY-MM-DD format")
    end_date: str = Field(description="The end date of the task in YYYY-MM-DD format")
    repeat: RepeatType = Field(description="The repeat type of the task")
    schedule: Union[SpecificType, OnWorkdayType, OnWeekendType, OnWeekdayType, OnMonthdayType, PeriodicType] = Field(description="The schedule of the task")

class SingleTimeAttribute(BaseModel):
    date: str = Field(description="The date of the task in YYYY-MM-DD format")

class TimeSeriesTask(BaseModel):
    task_name: str = Field(description="The name of the task")
    description: str = Field(description="The description of the task")
    task_duration: Union[SingleTimeAttribute, AcrossTimeAttribute] = Field(description="The duration type of the task")
    time_in_day: str = Field(description="The time of the day the task should be performed in HH:MM format")
    quantization: Union[Quantization, None] = Field(description="The quantization of the task")
    notes: str = Field(description="Give some notes of the task")

class Tasks(BaseModel):
    tasks_name: list[str] = Field(description="The name of the tasks")
    tasks: list[TimeSeriesTask] = Field(description="The list of tasks")

def get_time_series_data_tool_call(user_goal: str, user_plan: str, further_info: dict, final_plan: str) -> dict:

    system_prompt = (
        #"You are a helpful assistant that analyzes the final plan and generates the time series tasks list(due to the plan's content, generate 3-12 tasks)."
        "You are a helpful assistant that analyzes the final plan and generates the time series tasks list."
        "Step1: Analyze the final plan that how many tasks it needs to be done, then put the task names into the tasks_name list."
        "Step2: For each task, generate the details of the task, including the description, duration, time of the day, quantization, and notes."
        "*Make sure the tasks are independent and not overlapping with each other and cover all the plan's content."
        "*The tasks should be in the order of the plan's content."
    )    
    further_info_str = json.dumps(further_info)
    user_prompt = (
        "The user's goal:"
        f"{user_goal}"
        "The user's plan:"
        f"{user_plan}"
        "The further information:"
        f"{further_info_str}"
        "The final plan:"
        f"{final_plan}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    model = ChatOpenAI(model_name="gpt-4o", temperature=1.0)
    model = model.with_structured_output(Tasks)
    response = model.invoke(messages)
    return response.tasks