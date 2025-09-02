import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv()


def get_model_config():
    """
    Get model configuration based on environment variables.
    Priority: Vertex AI Gemini > Hosted Mistral > Local Model
    """
    if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        print("🧠 Using Vertex AI Gemini model")
        return os.environ.get("MODEL", "gemini-2.0-flash")

    elif os.environ.get("USE_LOCAL_MODEL", "").lower() == "true":
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


def google_search(query: str) -> dict:
    """
    Perform a Google search for the given query.
    Keep this function self-contained to avoid pickling issues.

    Args:
        query (str): The search query

    Returns:
        dict: Search results with status and results
    """
    # TODO: Implement actual Google search functionality
    # For now, return a placeholder
    return {
        "status": "success",
        "query": query,
        "results": [
            {
                "title": f"Search result for: {query}",
                "url": "https://example.com",
                "description": "This is a placeholder search result."
            }
        ]
    }


root_agent = Agent(
    name="google_search_agent",
    description="Answer questions using Google Search.",
    model=get_model_config(),
    instruction="""You are an expert researcher with access to Google Search tools. 
        You stick to facts and provide accurate, well-researched answers. 
        Always cite your sources when providing information from searches.
        If you cannot find reliable information, clearly state that.""",
    tools=[google_search]
)
