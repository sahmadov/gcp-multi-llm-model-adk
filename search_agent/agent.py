from google.adk import Agent
from google.adk.tools import google_search  # The Google Search tool
from google.adk.models.lite_llm import LiteLlm

import sys
sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
LiteLlm.debug = True

root_agent = Agent(
    name="google_search_agent",
    description="Answer questions using Google Search.",
    # Use openai/ prefix for LM Studio (OpenAI-compatible API)
    model=LiteLlm(
        model="mistralai/mistral-7b-instruct-v0.3",  # Changed prefix
        api_base="http://localhost:1234/v1",  # LM Studio default endpoint
        api_key="not-needed"  # LM Studio doesn't require API key
    ),
    instruction="You are an expert researcher. You stick to the facts.",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # tools=[google_search]
)