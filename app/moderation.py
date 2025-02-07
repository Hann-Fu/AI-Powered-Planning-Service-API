from langchain.chains import OpenAIModerationChain
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def check_policy(goal: str, plan: str) -> bool:
    """Uses OpenAI's Moderation API via LangChain to check content safety."""
    moderation_chain = OpenAIModerationChain(error_on_moderation=False, openai_api_key=OPENAI_API_KEY)
    result = moderation_chain.invoke(goal + plan)
    if result["output"] == "Text was found that violates OpenAI's content policy.":
        return False
    return True  # Returns False if prohibited content is found, True if safe