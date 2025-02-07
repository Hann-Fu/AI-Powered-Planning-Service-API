from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from pydantic import BaseModel, Field, ValidationError
from typing import List
import json
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------- Function Calling with Pydantic Schema ----------
class InfoNeeded(BaseModel):
    keyword: str = Field(description="A keyword of information needed")
    guide: str = Field(description="Instructions on what to provide")
    auto_gen: str = Field(description="An example text that could give users a reference")

class FurtherInfoResponse(BaseModel):
    flag: bool = Field(description="Indicates whether further information is needed")
    info_needed: List[InfoNeeded] = Field(description="List of additional information requirements")

further_info_schema = {
    "name": "further_info_analyzer",
    "description": "Analyze the user's input comprehensively to determine what crucial information is needed for creating a detailed, personalized plan.",
    "parameters": FurtherInfoResponse.model_json_schema()
}

def get_further_info_fc_pydantic_schema(user_goal: str, user_plan: str) -> FurtherInfoResponse:
    # TODO: Add start and end time request if not mentioned.
    # TODO: Add the personality of the user if not mentioned.
    # TODO: Control the scaling more concisely.

    system_prompt = (
        "You are a meticulous planning consultant whose expertise lies in helping users design comprehensive and actionable plans. "
        "Follow a clear, step-by-step reasoning process as outlined below:"
        "Initial Review:"
        "- Examine the user's provided information, including their goal, idea, or plan."
        "- Identify the key elements and the level of detail already provided."
        "Specificity Analysis:"
        "- Assess how specific the user's plan is."
        "- Determine what additional details are required to make the plan fully actionable."
        "- Decide on the number of follow-up questions needed (between 1 to 8) based on the current specificity."
        "Additional Information:"
        "- Analyze if the personality of the user and the start and end time of the user are necessary."
        "- IF the personality and start and end time of the user are not mentioned, add them to the list of questions needed."
        "Question Generation:"
        "- Create a targeted list of specific and actionable questions that gather the precise details necessary for plan creation."
        "- Ensure each question is directly relevant to the user's goal and adapts to different types of objectives."

        "- Focus on questions that are critical for finalizing the plan."
        "Your responses should clearly outline each step, ensuring the questions and insights you provide are precise, actionable, and tailored to the user's needs."
    )
    
    user_prompt = (
        "The information provided by the user:"
        f"Goal or Idea: {user_goal}"
        f"Plan: {user_plan or 'No plan provided.'}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    model = ChatOpenAI(model_name="gpt-4o", temperature=1.0, openai_api_key=OPENAI_API_KEY)

    response = model.invoke(
        messages,
        functions=[further_info_schema],
        function_call={"name": "further_info_analyzer"}
    )

    # Extract and validate the response
    fc = response.additional_kwargs.get("function_call")
    if not fc:
        raise ValueError("No function call was returned for further info analysis.")
    try:
        arguments = json.loads(fc.get("arguments", "{}"))
        validated_response = FurtherInfoResponse.model_validate(arguments)
        return validated_response
    except ValidationError as e:
        raise ValueError(f"Invalid response format from LLM: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in LLM response: {str(e)}")


# ---------- OpenAi Style Function Calling ---------- 

def get_further_info_fc(user_goal: str) -> dict:
    further_info_schema = {
        "name": "further_info_analyzer",
        "description": "Analyze the user's goal or plan to determine what further information is needed to tailor a plan."
                       "In addition, the user's personality should be considered. ",
        "parameters": {
            "type": "object",
            "properties": {
                "flag": {
                    "type": "boolean",
                    "description": "Indicates whether further information is needed."
                },
                "info_needed": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string", "description": "A keyword of information needed."},
                            "guide": {"type": "string", "description": "Instructions on what to provide."},
                            "auto_gen": {"type": "string", "description": "An example text that could give users a reference."}
                        },
                        "required": ["keyword", "guide", "auto_gen"]
                    },
                    "description": "List of additional information requirements for making a perfect plan.",
                    "additionalProperties": False
                },
                "strict": True
            },
            "required": ["flag", "info_needed"]
        }
    }

    # Build messages (using system and human messages)
    messages = [
        SystemMessage(content="You are a plan consultant who analyzes what further information is needed."),
        HumanMessage(content=f"User's goal/idea/plan: {user_goal}")
    ]

    # Initialize the ChatOpenAI model (using GPT-4o)
    chat = ChatOpenAI(model_name="gpt-4o-mini", temperature=1.0, openai_api_key=OPENAI_API_KEY)
    # Call the API with function calling enabled (forcing the call to further_info_analyzer)
    response = chat.invoke(
        messages,
        functions=[further_info_schema],
        function_call={"name": "further_info_analyzer"}
    )

    # Extract the function call data
    fc = response.additional_kwargs.get("function_call")
    if not fc:
        raise ValueError("No function call was returned for further info analysis.")
    arguments = fc.get("arguments")
    further_info = json.loads(arguments)
    return further_info

# ---------- Structured Output with JSON Schema ----------

def get_further_info_structured_output(user_goal: str, user_plan: str) -> dict:

    json_schema  = {
        "name": "further_info_analyzer",
        "description": "Analyze the user's input comprehensively to determine what crucial information is needed for creating a detailed, personalized plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "flag": {
                    "type": "boolean",
                    "description": "Indicates whether further information is needed."
                },
                "info_needed": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string", "description": "A keyword of information needed."},
                            "guide": {"type": "string", "description": "Instructions on what to provide."},
                            "auto_gen": {"type": "string", "description": "An example text that could give users a reference."}
                        },
                        "required": ["keyword", "guide", "auto_gen"]
                    },
                    "description": "List of additional information requirements for making a perfect plan.",
                    "additionalProperties": False
                },
                "strict": True
            },
            "required": ["flag", "info_needed"]
        }
    }

    system_prompt = (
        "You are a meticulous planning consultant whose expertise lies in helping users design comprehensive and actionable plans. "
        "Follow a clear, step-by-step reasoning process as outlined below:"
        "Initial Review:"
        "- Examine the user's provided information, including their goal, idea, or plan."
        "- Identify the key elements and the level of detail already provided."
        "Specificity Analysis:"
        "- Assess how specific the user's plan is."
        "- Determine what additional details are required to make the plan fully actionable."
        "- Decide on the number of follow-up questions needed (between 1 to 8) based on the current specificity."
        "Question Generation:"
        "- Create a targeted list of specific and actionable questions that gather the precise details necessary for plan creation."
        "- Ensure each question is directly relevant to the user's goal and adapts to different types of objectives."
        "- Focus on questions that are critical for finalizing the plan."
        "Your responses should clearly outline each step, ensuring the questions and insights you provide are precise, actionable, and tailored to the user's needs."
    )
    
    user_prompt = (
        "The information provided by the user:"
        f"Goal or Idea: {user_goal}"
        f"Plan: {user_plan or 'No plan provided.'}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]


    llm = ChatOpenAI(model_name="gpt-4o", temperature=1.0, openai_api_key=OPENAI_API_KEY)
    structured_llm = llm.with_structured_output(json_schema)
    response = structured_llm.invoke(messages)

    return response["info_needed"]