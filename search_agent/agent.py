import os
import sys

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from callback_logging import log_query_to_model, log_model_response

sys.path.append("..")
load_dotenv()


def get_model_config():
    """Use local if USE_LOCAL_MODEL=true, otherwise use hosted Mistral AI"""

    if os.environ.get("USE_LOCAL_MODEL", "").lower() == "true":
        print("🔧 Using LOCAL Mistral model")
        return LiteLlm(
            model=os.environ.get("LOCAL_MODEL", "mistral/mistralai/mistral-7b-instruct-v0.3"),
            api_base=os.environ.get("LOCAL_API_BASE", "http://localhost:1234/v1"),
            api_key="not-needed"
        )
    else:
        print("☁️ Using HOSTED Mistral AI")
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is required for hosted mode")

        return LiteLlm(
            model=os.environ.get("MISTRAL_MODEL", "mistral/mistral-small-latest"),
            api_key=api_key
        )


root_agent = Agent(
    name="google_search_agent",
    description="Answer questions using Google Search.",
    model=get_model_config(),
    instruction="You are an expert researcher. You stick to the facts.",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # tools=[google_search]
)
